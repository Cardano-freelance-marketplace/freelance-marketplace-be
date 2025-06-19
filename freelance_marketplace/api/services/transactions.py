import base64
import json
import subprocess
from typing import List, Optional, Any, Coroutine

from fastapi import HTTPException
from pycardano import *
from pycardano import TransactionBody

from freelance_marketplace.api.services.ogmios import Ogmios
from freelance_marketplace.core.config import settings
from freelance_marketplace.models.datums.default_datum import Milestone, DatumModel, MilestoneModel, \
    JobAgreement
from freelance_marketplace.models.redeemers.default_redeemer import DefaultRedeemer, ApproveMilestone, Refund, \
    RedeemMilestone

class TransactionBuilder:
    def __init__(self):
        self.network = settings.blockchain.network
        self.script = self.__load_script()
        self.context = Ogmios.get_context()

    async def __load_script(self) -> bytes:
        with open("scripts/job_agreement.plutus.json", "rb") as f:
            data = f.read()
        return data

    async def get_script_address(self) -> Address:
        plutus_script: PlutusV2Script = PlutusV2Script(await self.__load_script())
        script_hash: ScriptHash = plutus_script_hash(plutus_script)
        script_address = Address(payment_part=script_hash, network=settings.blockchain.network)
        return script_address

    async def get_plutus_script(self) -> PlutusV2Script:
        script_bytes: bytes = await self.__load_script()
        return PlutusV2Script(script_bytes)

    async def build_unsigned_tx(
            self,
            signer_address: Address,
            client_address: Address,
            freelancer_address: Address,
            milestone: dict,
            milestone_id: int,
            action: str = "create_milestone"
        ) -> TransactionBody:

        script_address = await self.get_script_address()
        utxo: UTxO = await Ogmios().get_utxo_by_milestone(milestone_id=milestone_id, script_address=script_address)
        if not utxo:
            raise HTTPException(status_code=404, detail="UTXO Milestone not found")

        datum: JobAgreement = await self.__build_datum(
            client_address=client_address,
            freelancer_address=freelancer_address,
            milestone=milestone,
        )
        script_outputs: List[TransactionOutput] = await self.__build_script_outputs(
            utxo=utxo,
            action=action,
            datum=datum,
            script_address=script_address,
            signer=signer_address
        )


        collateral_utxo: UTxO = await Ogmios().get_collateral_utxo(wallet_address=signer_address)
        if not collateral_utxo:
            raise HTTPException(status_code=404, detail="UTXO Collateral not found")

        redeemer_data = {
            "signer": signer_address.payment_part.payload,
            "is_client": True if signer_address == client_address else False,
            "is_freelancer": True if signer_address == freelancer_address else False
        }
        redeemer: PlutusData | None = await self.__build_redeemer(action=action, data=redeemer_data)

        return await self.__tx_builder(
            signer_address=signer_address,
            script_utxo=utxo,
            script_outputs=script_outputs,
            datum=datum,
            redeemer=redeemer,
            collateral_utxos=[
                collateral_utxo
            ]
        )

    async def __build_script_outputs(
            self,
            utxo: Optional[UTxO],
            action: str,
            datum: Optional[JobAgreement],
            script_address: Address,
            signer: Address
    ) -> List[TransactionOutput]:
        outputs = []

        if action.lower() == "create_milestone":
            output = TransactionOutput(
                address=script_address,
                amount=Value(datum.milestone.reward),
                datum=datum
            )
            min_ada = min_lovelace(await self.context, output, has_datum=True)
            if output.amount < min_ada:
                output.amount = Value(min_ada)
            outputs.append(output)

        elif action.lower() == "approve_milestone":
            # Create updated JobAgreement with approval toggled
            signer_bytes = signer.payment_part.payload
            if signer_bytes == datum.client:
                datum.milestone.approved_by_client = not datum.milestone.approved_by_client

            if signer_bytes == datum.freelancer:
                datum.milestone.approved_by_freelancer = not datum.milestone.approved_by_freelancer

            output = TransactionOutput(
                address=script_address,
                amount=utxo.output.amount,  # Keep same value
                datum=datum
            )
            outputs.append(output)

        elif action.lower() == "redeem_milestone":
            # Payout to freelancer
            reward = datum.milestone.reward
            outputs.append(TransactionOutput(
                address=Address.from_primitive(datum.freelancer),
                amount=Value(reward)
            ))

        elif action.lower() == "refund_milestone":
            # Refund to client
            refund = datum.milestone.reward
            outputs.append(TransactionOutput(
                address=Address.from_primitive(datum.client),
                amount=Value(refund)
            ))

        return outputs

    async def __build_datum(
            self,
            client_address: Address,
            freelancer_address: Address,
            milestone: dict
    ) -> JobAgreement:
        datum_model = DatumModel(
            freelancer=freelancer_address,
            client=client_address,
            milestone=MilestoneModel(**milestone)
        )

        datum: JobAgreement = JobAgreement(
            freelancer=datum_model.freelancer.payment_part.payload,
            client=datum_model.client.payment_part.payload,
            milestone=Milestone(
                reward=datum_model.milestone.reward,
                approved_by_freelancer=datum_model.milestone.approved_by_freelancer,
                approved_by_client=datum_model.milestone.approved_by_client,
                paid=datum_model.milestone.paid
            )
        )
        return datum

    async def __build_redeemer(
            self,
            action: str,
            data: dict
    ) -> PlutusData:
        redeemer = None
        if action == "create_milestone":
            redeemer = None
        elif action == "approve_milestone":
            redeemer = DefaultRedeemer(
                action=ApproveMilestone(),
                **data
            )
        elif action == "refund_milestone":
            redeemer = DefaultRedeemer(
                action=Refund(),
                **data
            )
        elif action == "redeem_milestone":
            redeemer = DefaultRedeemer(
                action=RedeemMilestone(),
                **data
            )
        return redeemer

    async def __tx_builder(
            self,
            signer_address: Address,
            script_utxo: Optional[UTxO],
            script_outputs: List[TransactionOutput],
            datum: PlutusData,
            redeemer: Optional[PlutusData],
            collateral_utxos: List[UTxO],
            extra_outputs: Optional[List[TransactionOutput]] = None
    ) -> TransactionBody:
        context = await Ogmios.get_context()
        builder = TransactionBuilder(context)

        # Add required signer (for script signature check)
        builder.required_signers = [
            VerificationKeyHash.from_primitive(signer_address.payment_part.payload)
        ]

        # If spending from script
        if script_utxo and redeemer:
            # Add the script input with datum and redeemer
            plutus_script = await self.get_plutus_script()
            builder.add_script_input(
                utxo=script_utxo,
                script=plutus_script,
                datum=datum,
                redeemer=redeemer
            )

            # Collateral
            builder.collaterals.extend(collateral_utxos)

        # Add script output (new state)
        for output in script_outputs:
            builder.add_output(output)

        # Add extra outputs (e.g. payment to freelancer)
        if extra_outputs:
            for out in extra_outputs:
                builder.add_output(out)

        builder.change_address = signer_address

        tx = builder.build()
        return tx

    async def sign_tx(self, tx_body: TransactionBody) -> Transaction:
        encrypted_skey_base64 = settings.wallet_keys.skey_encrypted
        encrypted_skey = base64.b64decode(encrypted_skey_base64)

        result = subprocess.run(
            ["gpg", "--decrypt"],
            input=encrypted_skey,
            capture_output=True,
            check=True
        )

        skey_json = json.loads(result.stdout)
        signing_key = PaymentSigningKey.from_json(skey_json)

        vkey_bytes = base64.b64decode(settings.wallet_keys.vkey)
        vkey_json = json.loads(vkey_bytes)
        vkey = PaymentVerificationKey.from_json(vkey_json)

        tx_hash = tx_body.hash()
        signature = signing_key.sign(tx_hash)

        vkey_witness = VerificationKeyWitness(
            signature=signature,
            vkey=vkey
        )

        witness_set = TransactionWitnessSet(vkey_witnesses=[vkey_witness])
        signed_tx = Transaction(
            transaction_body=tx_body,
            transaction_witness_set=witness_set
        )

        return signed_tx