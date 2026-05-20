from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.db import models

from app.routers import auth_routers
from app.routers import user_routers
from app.routers import address_router
from app.routers import user_card_router
from app.routers import history_router
from app.routers import analytics_router
from app.routers import forecast_router
from app.routers import realtime_router
from app.routers import notification_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app.include_router(auth_routers.router)
app.include_router(user_routers.router)
app.include_router(address_router.router)
app.include_router(user_card_router.router)
app.include_router(history_router.router)
app.include_router(analytics_router.router)
app.include_router(forecast_router.router)
app.include_router(realtime_router.router)
app.include_router(notification_router.router)
