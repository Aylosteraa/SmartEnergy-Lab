from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.models import (
    ElectricityMeterReading,
    SolarSystemReading
)


def get_energy_analytics(
    db: Session,
    days: int = 7
):

    consumption_data = (
        db.query(ElectricityMeterReading)
        .order_by(
            ElectricityMeterReading.timestamp.desc()
        )
        .limit(days * 24 * 6)
        .all()
    )

    solar_data = (
        db.query(SolarSystemReading)
        .order_by(
            SolarSystemReading.timestamp.desc()
        )
        .limit(days * 24 * 6)
        .all()
    )

    if not consumption_data:
        return {
            "has_data": False,
            "average_consumption": 0,
            "max_consumption": 0,
            "average_solar_generation": 0,
            "max_solar_generation": 0,
            "peak_consumption_hour": None,
            "peak_solar_hour": None
        }

    # -----------------------------
    # Споживання
    # -----------------------------

    consumption_values = [
        float(item.consumption_total or 0)
        for item in consumption_data
    ]

    average_consumption = (
        sum(consumption_values)
        / len(consumption_values)
    )

    max_consumption = max(
        consumption_values
    )

    # -----------------------------
    # Сонячна генерація
    # -----------------------------

    solar_values = [
        float(item.solar_generation or 0)
        for item in solar_data
    ]

    if solar_values:

        average_solar = (
            sum(solar_values)
            / len(solar_values)
        )

        max_solar = max(
            solar_values
        )

    else:

        average_solar = 0
        max_solar = 0

    # -----------------------------
    # Пікові години
    # -----------------------------

    consumption_by_hour = defaultdict(list)

    for item in consumption_data:

        if item.timestamp:

            consumption_by_hour[
                item.timestamp.hour
            ].append(
                float(
                    item.consumption_total or 0
                )
            )

    average_by_hour = {}

    for hour, values in consumption_by_hour.items():

        average_by_hour[hour] = (
            sum(values) / len(values)
        )

    peak_consumption_hour = None

    if average_by_hour:

        peak_consumption_hour = max(
            average_by_hour,
            key=average_by_hour.get
        )

    # -----------------------------
    # Пікова сонячна генерація
    # -----------------------------

    solar_by_hour = defaultdict(list)

    for item in solar_data:

        if item.timestamp:

            solar_by_hour[
                item.timestamp.hour
            ].append(
                float(
                    item.solar_generation or 0
                )
            )

    average_solar_by_hour = {}

    for hour, values in solar_by_hour.items():

        average_solar_by_hour[hour] = (
            sum(values) / len(values)
        )

    peak_solar_hour = None

    if average_solar_by_hour:

        peak_solar_hour = max(
            average_solar_by_hour,
            key=average_solar_by_hour.get
        )

    return {

        "has_data": True,

        "average_consumption":
        round(
            average_consumption,
            2
        ),

        "max_consumption":
        round(
            max_consumption,
            2
        ),

        "average_solar_generation":
        round(
            average_solar,
            2
        ),

        "max_solar_generation":
        round(
            max_solar,
            2
        ),

        "peak_consumption_hour":
        peak_consumption_hour,

        "peak_solar_hour":
        peak_solar_hour
    }