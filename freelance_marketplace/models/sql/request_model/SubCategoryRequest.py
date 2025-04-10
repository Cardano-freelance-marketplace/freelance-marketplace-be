from pydantic import BaseModel

class SubCategoryRequest(BaseModel):
    sub_category_name: str
    category_id: int
    sub_category_description: str