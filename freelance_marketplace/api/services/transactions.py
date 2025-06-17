import json
from typing import List, Optional
from pycardano import *

from freelance_marketplace.api.services.ogmios import Ogmios
from freelance_marketplace.core.config import settings
from freelance_marketplace.models.datums.default_datum import Milestone, DatumModel, MilestoneModel, \
    JobAgreement


class Transaction:
    def __init__(self):
        self.network = settings.blockchain.network
        self.script = self.__load_script()

    async def __load_script(self) -> PlutusV2Script:
        with open("scripts/job_agreement.plutus.json") as f:
            data = json.load(f)
        return PlutusV2Script(data["compiledCode"])

    async def get_script_address(self) -> Address:
        plutus_script: PlutusV2Script = await self.__load_script()
        script_hash: ScriptHash = plutus_script_hash(plutus_script)
        script_address = Address(payment_part=script_hash, network=settings.blockchain.network)
        return script_address



    async def build_unsigned_tx(
            self,
            requester_address: str,
            client_address: str,
            freelancer_address: str,
            milestone: dict,
            milestone_id: int

        ) -> Transaction:

        script_address = await self.get_script_address() ## STILL NEED TO GRAB THE INDEX OF THE UTXO
        utxo = await Ogmios().get_utxo_by_milestone(milestone_id=milestone_id, script_address=script_address)
        datum_model = DatumModel(
            freelancer=freelancer_address,
            client=client_address,
            milestone=MilestoneModel(**milestone)
        )

        datum: JobAgreement = JobAgreement(
            freelancer=bytes.fromhex(datum_model.freelancer),
            client=bytes.fromhex(datum_model.client),
            milestone=Milestone(
                reward=datum_model.milestone.reward,
                approved_by_freelancer=datum_model.milestone.approved_by_freelancer,
                approved_by_client=datum_model.milestone.approved_by_client,
                paid=datum_model.milestone.paid
            )
        )

        script_output = TransactionOutput(
            address=script_address,
            amount=Value(2_000_000),
            datum=datum
        )
        ## TODO build the redeemer and find a way to grab the collateral utxos aswell
        return await self.__tx_builder(
            signer_address=Address.from_primitive(requester_address), # User's wallet address
            script_utxo=TransactionInput.from_primitive([utxo["tx_hash"], utxo["output_index"]]), # UTXO sitting at validator ["f93a123456789abcdef...", 0]
            script_output=script_output,
            datum=datum,  # Replace with your actual datum
            redeemer=ConstrPlutusData(1, []),  # Replace with your actual redeemer
            collateral_utxos=[
                TransactionInput.from_primitive(["collateral_txhash", 0])
            ]
        )

    async def __tx_builder(
        self,
        signer_address: Address,
        script_utxo: TransactionInput,
        script_output: TransactionOutput,
        datum: PlutusData,
        redeemer: PlutusData,
        collateral_utxos: List[TransactionInput],
        extra_outputs: Optional[List[TransactionOutput]] = None
    ) -> Transaction:
        builder = TransactionBuilder(await Ogmios.get_context())

        # Add script input (validator UTXO)
        builder.add_script_input(
            script_utxo,
            script_output,
            self.script,
            datum=datum,
            redeemer=redeemer
        )

        # Add collateral
        for utxo in collateral_utxos:
            builder.add_collateral(utxo)

        # Optional extra outputs (like paying back to the validator, or paying rewards)
        if extra_outputs:
            for output in extra_outputs:
                builder.add_output(output)

        # Add change output to sender
        builder.add_change_address(signer_address)

        # Build the unsigned transaction
        tx = builder.build()

        return tx