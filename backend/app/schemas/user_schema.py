from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
# from app.schemas.meter_schema import MeterResponse
# from app.schemas.message_schema import MessageResponse

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str = Field(min_length=6)
    # serial_number: str

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

# class UserResponse(UserBase):
#     id: int
#     meters: Optional[List[MeterResponse]] = []
#     messages: Optional[List[MessageResponse]] = [] 

#     class Config:
#         from_attributes = True

class UserIDResponse(BaseModel):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str