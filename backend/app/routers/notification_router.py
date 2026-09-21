from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.db.database import SessionLocal
from app.db.models import Notification

from app.services.recomendation_service import (
    generate_energy_recommendations,
    get_day_recommendations
)

from app.schemas.test_notifications import (
    RecommendationTestRequest
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class NotificationCreate(BaseModel):

    user_id: int

    title: str

    message: str

    level: str = "info"


# =========================================================
# ОТРИМАТИ ВСІ NOTIFICATIONS
# =========================================================

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification)
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return notifications


# =========================================================
# СТВОРИТИ NOTIFICATION
# =========================================================

@router.post("/")
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db)
):
    notification = Notification(
        user_id=data.user_id,
        title=data.title,
        message=data.message,
        level=data.level
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification created",
        "notification": notification
    }


# =========================================================
# ВИДАЛИТИ NOTIFICATION
# =========================================================

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted"
    }


# =========================================================
# ПОЗНАЧИТИ ПРОЧИТАНИМ
# =========================================================

@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification marked as read",
        "notification": notification
    }


# =========================================================
# ОСТАННІ NOTIFICATIONS КОРИСТУВАЧА
# =========================================================

@router.get("/latest/{user_id}")
def get_latest_notifications(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return notifications


# =========================================================
# ТЕСТ РЕКОМЕНДАЦІЙ
# =========================================================

@router.post("/recommendations/test/{user_id}")
def test_recommendation(
    user_id: int,
    data: RecommendationTestRequest
):
    realtime_data = {
        "solar": data.realtime_data.solar.model_dump(),
        "battery": data.realtime_data.battery.model_dump(),
        "load": data.realtime_data.load.model_dump(),
        "meter": data.realtime_data.meter.model_dump()
    }

    # -----------------------------------------------------
    # Формуємо прогноз для тесту
    # -----------------------------------------------------

    forecast_data = None

    if data.forecast is not None:

        forecast_data = []

        for item in data.forecast:

            forecast_item = item.model_dump()

            # Якщо energy_balance не передали вручну,
            # він розраховується автоматично.
            if forecast_item["energy_balance"] is None:

                forecast_item["energy_balance"] = (
                    forecast_item["solar_generation"]
                    - forecast_item["total_consumption"]
                )

            forecast_data.append(
                forecast_item
            )

    # -----------------------------------------------------
    # Генеруємо рекомендацію
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        result = generate_energy_recommendations(
            db=db,
            user_id=user_id,
            realtime_data=realtime_data,
            forecast_data=forecast_data
        )

        return {
            "user_id": user_id,
            "realtime_data": realtime_data,
            "forecast": forecast_data,
            "recommendation": result
        }

    finally:
        db.close()


@router.get("/recommendations/day")
def get_day_recommendations_endpoint():

    recommendations = get_day_recommendations()

    return {
        "recommendations": recommendations
    }