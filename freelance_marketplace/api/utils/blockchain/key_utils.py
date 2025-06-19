import base64
import json
import subprocess

from pycardano import PaymentSigningKey, Key, PaymentVerificationKey, Address

from freelance_marketplace.core.config import settings


async def get_skey() -> PaymentSigningKey:
    encrypted_skey_base64 = settings.wallet_keys.skey_encrypted
    encrypted_skey = base64.b64decode(encrypted_skey_base64)

    result = subprocess.run(
        ["gpg", "--decrypt"],
        input=encrypted_skey,
        capture_output=True,
        check=True
    )

    skey_raw = result.stdout
    signing_key: PaymentSigningKey = PaymentSigningKey.from_json(skey_raw)
    return signing_key

async def get_vkey() -> PaymentVerificationKey:
    vkey_raw: bytes = base64.b64decode(settings.wallet_keys.vkey)
    vkey = PaymentVerificationKey.from_json(vkey_raw)
    return vkey

async def build_addr_from_vkey(vkey: PaymentVerificationKey) -> Address:
    return Address(payment_part=vkey.hash(), network=settings.blockchain.network)