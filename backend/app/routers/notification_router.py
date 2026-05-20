from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.db.models import Notification

from pydantic import BaseModel


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