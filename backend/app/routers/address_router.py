from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.address_schema import AddressCreate, AddressResponse
from app.repositories.address_repository import create_address

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.post(
    "/",
    response_model=AddressResponse
)
def create_new_address(
    data: AddressCreate,
    db: Session = Depends(get_db)
):

    return create_address(
        db,
        data
    )