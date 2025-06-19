import os
from pycardano import PaymentSigningKey, PaymentVerificationKey

def generate_credentials():
    # Path to save
    wallet_dir = os.path.expanduser("~/Documents/security/wallet_credentials")
    os.makedirs(wallet_dir, exist_ok=True)

    # Generate keys
    signing_key = PaymentSigningKey.generate()
    verification_key = PaymentVerificationKey.from_signing_key(signing_key)

    # Write signing key
    with open(os.path.join(wallet_dir, "payment.skey"), "w") as f:
        f.write(signing_key.to_json())

    # Write verification key
    with open(os.path.join(wallet_dir, "payment.vkey"), "w") as f:
        f.write(verification_key.to_json())

if __name__ == "__main__":
    generate_credentials()