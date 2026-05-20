from pydantic import BaseModel


class AddressCreate(BaseModel):

    city: str
    street: str

    electricity_meter_serial: str

    solar_system_serial: str


class AddressResponse(BaseModel):

    id: int
    city: str
    street: str

    class Config:
        from_attributes = True
