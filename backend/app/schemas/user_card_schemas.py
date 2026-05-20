from pydantic import BaseModel
from datetime import datetime

class UserCardCreate(BaseModel):
    title: str
    city: str
    street: str


class UserCardResponse(BaseModel):
    id: int
    title: str
    city: str
    street: str

    class Config:
        from_attributes = True