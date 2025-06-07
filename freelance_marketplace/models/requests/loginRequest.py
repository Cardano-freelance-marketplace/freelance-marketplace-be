from pydantic import BaseModel


class LoginRequest(BaseModel):
    wallet_address: str
    signature: str
    nonce: str
    public_key_hex: str
    wallet_type_name: str = None
