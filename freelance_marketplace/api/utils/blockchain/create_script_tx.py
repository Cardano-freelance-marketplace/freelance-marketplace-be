from pycardano import Address
from freelance_marketplace.api.services.transactions import Transaction

async def generate_unsigned_tx():
    tx = Transaction()
    signer_address: Address = await tx.get_script_address()
    client_address: Address = signer_address
    freelancer_address: Address = signer_address
    milestone_id: int = 0
    milestone: dict = {
        "milestone_id": milestone_id,
        "reward": 0,
        "approved_by_freelancer": "False",
        "approved_by_client": "False",
        "paid": "False",
    }
    unsigned_tx = await tx.build_unsigned_tx(
        signer_address=signer_address,
        client_address=client_address,
        freelancer_address=freelancer_address,
        milestone=milestone,
        milestone_id=milestone_id,
    )
    return unsigned_tx

if __name__ == "__main__":
    generate_unsigned_tx()