from fastapi import APIRouter

from app.services.forecast_service import (

    forecast_24h,

    forecast_7d,

    forecast_month,

    generate_recommendations
)

router = APIRouter(

    prefix="/forecast",

    tags=["Forecast"]
)

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
def get_recommendations():

    return generate_recommendations()