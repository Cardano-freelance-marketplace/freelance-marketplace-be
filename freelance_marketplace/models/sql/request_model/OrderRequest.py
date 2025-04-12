from pydantic import BaseModel


class OrderRequest(BaseModel):
    client_id: int