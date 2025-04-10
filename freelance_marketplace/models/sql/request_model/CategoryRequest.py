from pydantic import BaseModel


class CategoryRequest(BaseModel):
    category_description: str
    category_name: str