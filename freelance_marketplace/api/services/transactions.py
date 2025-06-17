import json
from typing import List, Optional
from pycardano import *

from freelance_marketplace.api.services.ogmios import Ogmios
from freelance_marketplace.core.config import settings


class Transaction():
    def __init__(self):
        self.network = settings.blockchain.network
        self.script = self.__load_script()


    async def __load_script(self) -> PlutusV2Script:
        with open("scripts/job_agreement.plutus.json") as f:
            data = json.load(f)
        return PlutusV2Script(data["compiledCode"])

    async def __get_script_address(self) -> Address:
        plutus_script: PlutusV2Script = await self.__load_script()
        script_hash: ScriptHash = plutus_script_hash(plutus_script)
        script_address = Address(payment_part=script_hash, network=settings.blockchain.network)
        return script_address

    async def build_unsined_tx(self,
                         action: str = "ApproveMilestone",
                         wallet_address: Optional[str] = None
     ) -> Transaction:
        script_utxo = self.__get_script_address() ## STILL NEED TO GRAB THE INDEX OF THE UTXO

        # return await self.__tx_builder(
        #     signer_address=Address.from_primitive(wallet_address), # User's wallet address
        #     script_utxo=TransactionInput.from_primitive(["txhash", 0]), # UTXO sitting at validator ["f93a123456789abcdef...", 0]
        #     script_output=TransactionOutput(
        #         Address.from_primitive("addr_test1..."),
        #         Value(2_000_000),
        #         datum_hash=None  # Only needed if datum is off-chain
        #     ), # GRAB THIS FROM OGMIOS, QUERY THE UTXO AND GET THAT DATUM CONTENT AND PASTE IT HERE
        #     datum=ConstrPlutusData(0, []),  # Replace with your actual datum
        #     redeemer=ConstrPlutusData(1, []),  # Replace with your actual redeemer
        #     collateral_utxos=[
        #         TransactionInput.from_primitive(["collateral_txhash", 0])
        #     ]
        # )

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