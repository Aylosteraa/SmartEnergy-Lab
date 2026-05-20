from sqlalchemy.orm import Session

from app.db.models import (
    UserCard,
    Address
)

# GET ALL USER CARDS

def get_user_cards(
    db: Session,
    user_id: int
):

    cards = (
        db.query(UserCard)
        .filter(UserCard.user_id == user_id)
        .all()
    )

    result = []

    for card in cards:

        result.append({
            "id": card.id,
            "title": card.title,
            "created_at": card.created_at,
            "city": card.address.city,
            "street": card.address.street
        })

    return result


# GET ONE CARD

def get_user_card(
    db: Session,
    card_id: int,
    user_id: int
):

    card = (
        db.query(UserCard)
        .filter(
            UserCard.id == card_id,
            UserCard.user_id == user_id
        )
        .first()
    )

    if not card:
        return None

    return {
        "id": card.id,
        "title": card.title,
        "created_at": card.created_at,
        "city": card.address.city,
        "street": card.address.street
    }


# CREATE USER CARD

def create_user_card(
    db: Session,
    user_id: int,
    data
):

    # SEARCH ADDRESS

    address = (
        db.query(Address)
        .filter(
            Address.city == data.city,
            Address.street == data.street
        )
        .first()
    )

    # ADDRESS NOT FOUND

    if not address:
        return None

    # CREATE CARD

    card = UserCard(
        title=data.title,
        user_id=user_id,
        address_id=address.id
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "title": card.title,
        "created_at": card.created_at,
        "city": address.city,
        "street": address.street
    }


def delete_user_card(
    db: Session,
    card_id: int,
    user_id: int
):

    card = (
        db.query(UserCard)
        .filter(
            UserCard.id == card_id,
            UserCard.user_id == user_id
        )
        .first()
    )

    if not card:
        return None

    db.delete(card)
    db.commit()

    return True