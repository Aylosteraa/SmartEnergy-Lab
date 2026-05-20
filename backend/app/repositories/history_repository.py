from sqlalchemy.orm import Session

from sqlalchemy import extract, func

from app.db.models import (
    ElectricityMeterReading,
    SolarSystemReading,
    Address,
    UserCard,
    ElectricityMeter,
    SolarSystem
)


# GET METER

def get_meter_and_solar_ids(
    db: Session,
    card_id: int
):

    card = (
        db.query(UserCard)
        .filter(UserCard.id == card_id)
        .first()
    )

    address_id = card.address_id

    meter = (
        db.query(ElectricityMeter)
        .filter(
            ElectricityMeter.address_id ==
            address_id
        )
        .first()
    )

    solar = (
        db.query(SolarSystem)
        .filter(
            SolarSystem.address_id ==
            address_id
        )
        .first()
    )

    return meter.id, solar.id


# MONTH

def get_month_history(
    db: Session,
    card_id: int,
    history_type: str
):

    meter_id, solar_id = (
        get_meter_and_solar_ids(
            db,
            card_id
        )
    )

    # TOTAL

    if history_type == "total":

        query = (
            db.query(
                extract(
                    "day",
                    ElectricityMeterReading.timestamp
                ).label("day"),

                func.sum(
                    ElectricityMeterReading.consumption_total
                ).label("value")
            )

            .filter(
                ElectricityMeterReading.electricity_meter_id
                == meter_id
            )

            .group_by("day")

            .order_by("day")
        )

    # SOLAR

    elif history_type == "solar":

        query = (
            db.query(
                extract(
                    "day",
                    ElectricityMeterReading.timestamp
                ).label("day"),

                func.sum(
                    ElectricityMeterReading.consumption_solar
                ).label("value")
            )

            .filter(
                ElectricityMeterReading.electricity_meter_id
                == meter_id
            )

            .group_by("day")

            .order_by("day")
        )

    # BATTERY

    elif history_type == "battery":

        query = (
            db.query(
                extract(
                    "day",
                    ElectricityMeterReading.timestamp
                ).label("day"),

                func.sum(
                    ElectricityMeterReading.consumption_battery
                ).label("value")
            )

            .filter(
                ElectricityMeterReading.electricity_meter_id
                == meter_id
            )

            .group_by("day")

            .order_by("day")
        )

    # GENERATION

    elif history_type == "generation":

        query = (
            db.query(
                extract(
                    "day",
                    SolarSystemReading.timestamp
                ).label("day"),

                func.sum(
                    SolarSystemReading.solar_generation
                ).label("value")
            )

            .filter(
                SolarSystemReading.solar_system_id
                == solar_id
            )

            .group_by("day")

            .order_by("day")
        )

    else:

        return []

    result = []

    for row in query.all():

        result.append({
            "label": str(int(row.day)),
            "value": float(row.value)
        })

    return result


def get_week_history(
    db: Session,
    card_id: int,
    history_type: str
):

    meter_id, solar_id = (
        get_meter_and_solar_ids(
            db,
            card_id
        )
    )

    weekdays = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ]

    if history_type == "generation":

        query = (
            db.query(
                extract(
                    "dow",
                    SolarSystemReading.timestamp
                ).label("dow"),

                func.sum(
                    SolarSystemReading.solar_generation
                ).label("value")
            )

            .filter(
                SolarSystemReading.solar_system_id
                == solar_id
            )

            .group_by("dow")

            .order_by("dow")
        )

    else:

        field = (
            ElectricityMeterReading.consumption_total
        )

        if history_type == "solar":
            field = (
                ElectricityMeterReading.consumption_solar
            )

        elif history_type == "battery":
            field = (
                ElectricityMeterReading.consumption_battery
            )

        query = (
            db.query(
                extract(
                    "dow",
                    ElectricityMeterReading.timestamp
                ).label("dow"),

                func.sum(field).label("value")
            )

            .filter(
                ElectricityMeterReading.electricity_meter_id
                == meter_id
            )

            .group_by("dow")

            .order_by("dow")
        )

    result = []

    for row in query.all():

        idx = int(row.dow)

        result.append({
            "label": weekdays[idx],
            "value": float(row.value)
        })

    return result

def get_year_history(
    db: Session,
    card_id: int,
    history_type: str
):

    meter_id, solar_id = (
        get_meter_and_solar_ids(
            db,
            card_id
        )
    )

    months = [
        "Jan", "Feb", "Mar",
        "Apr", "May", "Jun",
        "Jul", "Aug", "Sep",
        "Oct", "Nov", "Dec"
    ]

    if history_type == "generation":

        query = (
            db.query(
                extract(
                    "month",
                    SolarSystemReading.timestamp
                ).label("month"),

                func.sum(
                    SolarSystemReading.solar_generation
                ).label("value")
            )

            .filter(
                SolarSystemReading.solar_system_id
                == solar_id
            )

            .group_by("month")

            .order_by("month")
        )

    else:

        field = (
            ElectricityMeterReading.consumption_total
        )

        if history_type == "solar":
            field = (
                ElectricityMeterReading.consumption_solar
            )

        elif history_type == "battery":
            field = (
                ElectricityMeterReading.consumption_battery
            )

        query = (
            db.query(
                extract(
                    "month",
                    ElectricityMeterReading.timestamp
                ).label("month"),

                func.sum(field).label("value")
            )

            .filter(
                ElectricityMeterReading.electricity_meter_id
                == meter_id
            )

            .group_by("month")

            .order_by("month")
        )

    result = []

    for row in query.all():

        idx = int(row.month) - 1

        result.append({
            "label": months[idx],
            "value": float(row.value)
        })

    return result