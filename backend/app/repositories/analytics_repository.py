from sqlalchemy.orm import Session

from sqlalchemy import extract, func

from app.db.models import (
    ElectricityMeterReading,
    SolarSystemReading,
    UserCard,
    ElectricityMeter,
    SolarSystem
)


# GET IDS

def get_ids(
    db: Session,
    card_id: int
):

    card = (
        db.query(UserCard)
        .filter(UserCard.id == card_id)
        .first()
    )

    meter = (
        db.query(ElectricityMeter)
        .filter(
            ElectricityMeter.address_id ==
            card.address_id
        )
        .first()
    )

    solar = (
        db.query(SolarSystem)
        .filter(
            SolarSystem.address_id ==
            card.address_id
        )
        .first()
    )

    return meter.id, solar.id

def get_analytics(
    db: Session,
    card_id: int,
    period: str,
    analytics_type: str
):

    meter_id, solar_id = get_ids(
        db,
        card_id
    )

    # CONFIG

    model = ElectricityMeterReading

    field = (
        ElectricityMeterReading.consumption_total
    )

    entity_id = meter_id

    entity_field = (
        ElectricityMeterReading.electricity_meter_id
    )

    if analytics_type == "solar":

        field = (
            ElectricityMeterReading.consumption_solar
        )

    elif analytics_type == "battery":

        field = (
            ElectricityMeterReading.consumption_battery
        )

    elif analytics_type == "generation":

        model = SolarSystemReading

        field = (
            SolarSystemReading.solar_generation
        )

        entity_id = solar_id

        entity_field = (
            SolarSystemReading.solar_system_id
        )

    # GROUPING

    if period == "week":

        group = extract(
            "dow",
            model.timestamp
        )

        labels = [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ]

    elif period == "month":

        group = extract(
            "day",
            model.timestamp
        )

        labels = None

    else:

        group = extract(
            "month",
            model.timestamp
        )

        labels = [
            "Jan", "Feb", "Mar",
            "Apr", "May", "Jun",
            "Jul", "Aug", "Sep",
            "Oct", "Nov", "Dec"
        ]

    # CHART

    chart_query = (

        db.query(

            group.label("group"),

            func.avg(field).label("value")
        )

        .filter(
            entity_field == entity_id
        )

        .group_by("group")

        .order_by("group")
    )

    chart = []

    values = []

    for row in chart_query.all():

        values.append(
            float(row.value)
        )

        if labels:

            label = labels[
                int(row.group) - 1
            ]

        else:

            label = str(
                int(row.group)
            )

        chart.append({
            "label": label,
            "value": float(row.value)
        })

    # STATS

    stats_query = (

        db.query(

            func.avg(field),

            func.min(field),

            func.max(field)
        )

        .filter(
            entity_field == entity_id
        )

        .first()
    )

    return {
        "chart": chart,

        "stats": {

            "avg": round(
                float(stats_query[0]),
                2
            ),

            "min": round(
                float(stats_query[1]),
                2
            ),

            "max": round(
                float(stats_query[2]),
                2
            )
        }
    }

