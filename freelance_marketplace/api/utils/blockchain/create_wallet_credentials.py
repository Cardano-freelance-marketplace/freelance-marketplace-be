import os

from pycardano import PaymentSigningKey, PaymentVerificationKey

# Path to save
wallet_dir = os.path.expanduser("~/Documents/security/wallet_credentials")
os.makedirs(wallet_dir, exist_ok=True)

# Generate keys
signing_key = PaymentSigningKey.generate()
verification_key = PaymentVerificationKey.from_signing_key(signing_key)

# Write signing key
with open(os.path.join(wallet_dir, "payment.skey"), "w") as f:
    f.write(signing_key.to_cbor_hex())

# Write verification key
with open(os.path.join(wallet_dir, "payment.vkey"), "w") as f:
    f.write(verification_key.to_cbor_hex())