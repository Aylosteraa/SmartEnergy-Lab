import pandas as pd
import numpy as np
import random

from datetime import datetime

from app.db.models import (
    ElectricityMeterReading,
    SolarSystemReading
)


def generate_historical_readings(
    db,
    electricity_meter_id,
    solar_system_id
):

    START_DATE = "2025-04-30"

    END_DATE = "2026-05-18"

    FREQ = "1h"

    np.random.seed(42)

    random.seed(42)


    date_range = pd.date_range(
        start=START_DATE,
        end=END_DATE,
        freq=FREQ
    )

    df = pd.DataFrame({
        "Datetime": date_range
    })


    df["month"] = df["Datetime"].dt.month

    df["day"] = df["Datetime"].dt.day

    df["hour"] = df["Datetime"].dt.hour

    df["day_of_week"] = (
        df["Datetime"].dt.dayofweek
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)


    df["temp_dry"] = (
        10
        + 10 * np.sin(
            2 * np.pi * df["hour"] / 24
        )
        + np.random.normal(0, 2, len(df))
    )

    df["cloudiness"] = np.clip(
        np.random.normal(50, 25, len(df)),
        0,
        100
    )

    df["humidity"] = np.clip(
        np.random.normal(60, 15, len(df)),
        20,
        100
    )

    df["wind_speed"] = np.clip(
        np.random.normal(5, 2, len(df)),
        0,
        20
    )

    solar_generation = []

    for _, row in df.iterrows():

        hour = row["hour"]

        cloudiness = row["cloudiness"]

        if hour < 6 or hour > 20:

            generation = 0

        else:

            solar_factor = np.sin(
                np.pi * (hour - 6) / 14
            )

            cloud_factor = (
                1 - (cloudiness / 100)
            )

            generation = (
                solar_factor
                * cloud_factor
                * random.uniform(2, 6)
            )

        solar_generation.append(
            max(generation, 0)
        )

    df["solar_generation"] = (
        solar_generation
    )

    consumption_total = []

    for _, row in df.iterrows():

        base = random.uniform(1.5, 4)

        if 18 <= row["hour"] <= 23:

            base += random.uniform(1, 3)

        if 6 <= row["hour"] <= 9:

            base += random.uniform(0.5, 2)

        if row["is_weekend"]:

            base += random.uniform(0.3, 1)

        consumption_total.append(base)

    df["consumption_total"] = (
        consumption_total
    )

    grid_usage = []

    solar_usage = []

    battery_usage = []

    battery_level = 70

    battery_levels = []

    for _, row in df.iterrows():

        total = row["consumption_total"]

        solar_gen = row["solar_generation"]

        solar = min(total, solar_gen)

        remaining = total - solar

        battery = 0

        if remaining > 0 and battery_level > 20:

            battery = min(
                remaining,
                random.uniform(
                    0.2,
                    remaining
                )
            )

        grid = remaining - battery

        battery_level += (
            solar_gen * 0.3
        )

        battery_level -= (
            battery * 0.5
        )

        battery_level = np.clip(
            battery_level,
            0,
            100
        )

        grid_usage.append(grid)

        solar_usage.append(solar)

        battery_usage.append(battery)

        battery_levels.append(
            battery_level
        )

    df["consumption_grid"] = (
        grid_usage
    )

    df["consumption_solar"] = (
        solar_usage
    )

    df["consumption_battery"] = (
        battery_usage
    )

    df["battery_level"] = (
        battery_levels
    )

    meter_readings = []

    solar_readings = []

    for _, row in df.iterrows():

        meter_reading = (
            ElectricityMeterReading(

                electricity_meter_id=
                electricity_meter_id,

                consumption_total=
                row["consumption_total"],

                consumption_grid=
                row["consumption_grid"],

                consumption_solar=
                row["consumption_solar"],

                consumption_battery=
                row["consumption_battery"],

                temp_dry=
                row["temp_dry"],

                cloudiness=
                row["cloudiness"],

                humidity=
                row["humidity"],

                wind_speed=
                row["wind_speed"],

                timestamp=
                row["Datetime"]
            )
        )

        solar_reading = (
            SolarSystemReading(

                solar_system_id=
                solar_system_id,

                solar_generation=
                row["solar_generation"],

                battery_level=
                row["battery_level"],

                temp_dry=
                row["temp_dry"],

                cloudiness=
                row["cloudiness"],

                humidity=
                row["humidity"],

                wind_speed=
                row["wind_speed"],

                timestamp=
                row["Datetime"]
            )
        )

        meter_readings.append(
            meter_reading
        )

        solar_readings.append(
            solar_reading
        )

    db.bulk_save_objects(
        meter_readings
    )

    db.bulk_save_objects(
        solar_readings
    )

    db.commit()

    print(
        "Historical readings generated."
    )