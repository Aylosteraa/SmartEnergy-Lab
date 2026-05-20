from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.repositories.analytics_repository import (
    get_analytics
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/")
def analytics(
    card_id: int,
    period: str,
    analytics_type: str,
    db: Session = Depends(get_db)
):

    return get_analytics(
        db,
        card_id,
        period,
        analytics_type
    )