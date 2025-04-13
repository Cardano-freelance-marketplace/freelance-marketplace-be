from pydantic import BaseModel


class TransactionRequest(BaseModel):
    amount: int
    token_name: str = "ADA"
    deleted: bool = False
    receiver_address: str
    client_id: int
    freelancer_id: int