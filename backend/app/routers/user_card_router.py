from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.user_card_schemas import (
    UserCardCreate,
    UserCardResponse
)

from app.repositories.user_card_repository import (
    get_user_cards,
    get_user_card,
    create_user_card,
    delete_user_card
)

from app.routers.user_routers import get_current_user


router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)


@router.get(
    "/",
    response_model=list[UserCardResponse]
)
def get_cards(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return get_user_cards(
        db,
        current_user.id
    )


@router.get(
    "/{card_id}",
    response_model=UserCardResponse
)
def get_one_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    card = get_user_card(
        db,
        card_id,
        current_user.id
    )

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Card not found"
        )

    return card


@router.post(
    "/",
    response_model=UserCardResponse
)
def create_card(
    data: UserCardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    card = create_user_card(
        db,
        current_user.id,
        data
    )

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    return card


@router.delete("/{card_id}")
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    deleted = delete_user_card(
        db,
        card_id,
        current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Card not found"
        )

    return {
        "message": "Card deleted"
    }