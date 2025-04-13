from pydantic import BaseModel


class LoginRequest(BaseModel):
    wallet_address: str
    public_key: str
    signature: str
    signed_nonce: str
    wallet_type_name: str
