from sqlalchemy.orm import Session

from app.db.models import Address, ElectricityMeter, SolarSystem
from app.services.generate_service import generate_historical_readings

def find_address(
    db: Session,
    city: str,
    street: str
):

    return (
        db.query(Address)
        .filter(
            Address.city == city,
            Address.street == street
        )
        .first()
    )


def create_address(
    db: Session,
    data
):

    # перевіряємо чи існує адреса
    existing_address = find_address(
        db,
        data.city,
        data.street
    )

    if existing_address:
        return existing_address

    # CREATE ADDRESS

    address = Address(
        city=data.city,
        street=data.street
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    # CREATE ELECTRICITY METER

    electricity_meter = ElectricityMeter(
        serial_number=data.electricity_meter_serial,
        address_id=address.id
    )

    db.add(electricity_meter)

    # CREATE SOLAR SYSTEM

    solar_system = SolarSystem(
        serial_number=data.solar_system_serial,
        address_id=address.id
    )

    db.add(solar_system)

    db.commit()

    db.refresh(electricity_meter)

    db.refresh(solar_system)

    generate_historical_readings(
        db,
        electricity_meter.id,
        solar_system.id
    )

    return address