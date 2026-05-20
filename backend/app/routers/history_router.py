from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.repositories.history_repository import (
    get_month_history,
    get_week_history,
    get_year_history
)

router = APIRouter(
    prefix="/history",
    tags=["History"]
)


# =========================================
# MONTH
# =========================================

@router.get("/month")
def month_history(
    card_id: int,
    history_type: str,
    db: Session = Depends(get_db)
):

    return get_month_history(
        db,
        card_id,
        history_type
    )


# =========================================
# WEEK
# =========================================

@router.get("/week")
def week_history(
    card_id: int,
    history_type: str,
    db: Session = Depends(get_db)
):

    return get_week_history(
        db,
        card_id,
        history_type
    )


# =========================================
# YEAR
# =========================================

@router.get("/year")
def year_history(
    card_id: int,
    history_type: str,
    db: Session = Depends(get_db)
):

    return get_year_history(
        db,
        card_id,
        history_type
    )