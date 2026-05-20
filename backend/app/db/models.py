from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    cards = relationship(
        "UserCard",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)

    city = Column(String(100), nullable=False)

    street = Column(String(100), nullable=False)

    cards = relationship(
        "UserCard",
        back_populates="address"
    )

    electricity_meter = relationship(
        "ElectricityMeter",
        back_populates="address",
        uselist=False,
        cascade="all, delete-orphan"
    )

    solar_system = relationship(
        "SolarSystem",
        back_populates="address",
        uselist=False,
        cascade="all, delete-orphan"
    )

class UserCard(Base):
    __tablename__ = "user_cards"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="cards"
    )

    address = relationship(
        "Address",
        back_populates="cards"
    )

class ElectricityMeter(Base):
    __tablename__ = "electricity_meters"

    id = Column(Integer, primary_key=True, index=True)

    serial_number = Column(String(100), unique=True, nullable=False)

    address_id = Column(
        Integer,
        ForeignKey("addresses.id"),
        unique=True,
        nullable=False
    )

    address = relationship(
        "Address",
        back_populates="electricity_meter"
    )


class SolarSystem(Base):
    __tablename__ = "solar_systems"

    id = Column(Integer, primary_key=True, index=True)

    serial_number = Column(String(100), unique=True, nullable=False)

    address_id = Column(
        Integer,
        ForeignKey("addresses.id"),
        unique=True,
        nullable=False
    )

    address = relationship(
        "Address",
        back_populates="solar_system"
    )

class ElectricityMeterReading(Base):

    __tablename__ = "electricity_meter_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    electricity_meter_id = Column(
        Integer,
        ForeignKey("electricity_meters.id"),
        nullable=False
    )
    consumption_total = Column(Float)

    consumption_grid = Column(Float)

    consumption_solar = Column(Float)

    consumption_battery = Column(Float)

    temp_dry = Column(Float)

    cloudiness = Column(Float)

    humidity = Column(Float)

    wind_speed = Column(Float)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    electricity_meter = relationship(
        "ElectricityMeter"
    )


class SolarSystemReading(Base):

    __tablename__ = "solar_system_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    solar_system_id = Column(
        Integer,
        ForeignKey("solar_systems.id"),
        nullable=False
    )

    solar_generation = Column(Float)

    battery_level = Column(Float)

    temp_dry = Column(Float)

    cloudiness = Column(Float)

    humidity = Column(Float)

    wind_speed = Column(Float)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    solar_system = relationship(
        "SolarSystem"
    )

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    level = Column(
        String,
        default="info"
    )

    is_read = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship("User")