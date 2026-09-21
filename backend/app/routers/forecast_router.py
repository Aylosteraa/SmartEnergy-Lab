from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.services.forecast_service import (
    forecast_24h,
    forecast_7d,
    forecast_month
)

from app.services.recomendation_service import (
    get_forecast_recommendations,
    get_analytics_recommendations
)


router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/24h")
def get_24h_forecast():

    return forecast_24h()


@router.get("/7d")
def get_7d_forecast():

    return forecast_7d()


@router.get("/month")
def get_month_forecast():

    return forecast_month()


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db)
):

    return {

        "forecast":
        get_forecast_recommendations(),

        "analytics":
        get_analytics_recommendations(
            db
        )
    }