from datetime import (
    datetime,
    timedelta
)

import pandas as pd

import numpy as np

import joblib


total_model = joblib.load(
    "app/ml/models/total_model.pkl"
)

solar_model = joblib.load(
    "app/ml/models/solar_model.pkl"
)

battery_model = joblib.load(
    "app/ml/models/battery_model.pkl"
)

generation_model = joblib.load(
    "app/ml/models/generation_model.pkl"
)


def generate_weather_features(
    dt: datetime
):

    hour = dt.hour

    temp = (
        15
        + 10 * np.sin(
            2 * np.pi * hour / 24
        )
        + np.random.normal(0, 1)
    )

    cloudiness = np.clip(

        50
        + 20 * np.sin(
            2 * np.pi * hour / 24
        )
        + np.random.normal(0, 10),

        0,
        100
    )

    humidity = np.clip(

        60
        + np.random.normal(0, 5),

        20,
        100
    )

    wind_speed = np.clip(

        5
        + np.random.normal(0, 1),

        0,
        20
    )

    return {

        "temp_dry": temp,

        "cloudiness": cloudiness,

        "humidity": humidity,

        "wind_speed": wind_speed
    }


def create_features(
    dt: datetime
):

    weather = (
        generate_weather_features(dt)
    )

    features = {

        "month": dt.month,

        "day": dt.day,

        "hour": dt.hour,

        "day_of_week":
        dt.weekday(),

        "is_weekend":
        int(dt.weekday() >= 5),

        "temp_dry":
        weather["temp_dry"],

        "cloudiness":
        weather["cloudiness"],

        "humidity":
        weather["humidity"],

        "wind_speed":
        weather["wind_speed"],

        # mock lag features
        "lag_24h":
        np.random.uniform(2, 5),

        "rolling_24h":
        np.random.uniform(2, 5)
    }

    return pd.DataFrame([features])


def forecast_24h():

    now = datetime.now()

    result = []

    for i in range(24):

        future_time = (
            now + timedelta(hours=i)
        )

        X = create_features(
            future_time
        )

        total = (
            total_model.predict(X)[0]
        )

        solar = (
            solar_model.predict(X)[0]
        )

        battery = (
            battery_model.predict(X)[0]
        )

        generation = (
            generation_model.predict(X)[0]
        )

        result.append({

            "time":
            future_time.strftime("%H:%M"),

            "total_consumption":
            round(float(total), 2),

            "solar_consumption":
            round(float(solar), 2),

            "battery_consumption":
            round(float(battery), 2),

            "solar_generation":
            round(float(generation), 2)
        })

    return result


def forecast_7d():

    now = datetime.now()

    result = []

    for i in range(7):

        future_time = (
            now + timedelta(days=i)
        ).replace(hour=13)

        X = create_features(
            future_time
        )

        total = (
            total_model.predict(X)[0]
        )

        solar = (
            solar_model.predict(X)[0]
        )

        battery = (
            battery_model.predict(X)[0]
        )

        generation = (
            generation_model.predict(X)[0]
        )

        result.append({

            "date":
            future_time.strftime("%Y-%m-%d"),

            "total_consumption":
            round(float(total), 2),

            "solar_consumption":
            round(float(solar), 2),

            "battery_consumption":
            round(float(battery), 2),

            "solar_generation":
            round(float(generation), 2)
        })

    return result


def forecast_month():

    now = datetime.now()

    result = []

    for i in range(30):

        future_time = (
            now + timedelta(days=i)
        ).replace(hour=13)

        X = create_features(
            future_time
        )

        total = (
            total_model.predict(X)[0]
        )

        solar = (
            solar_model.predict(X)[0]
        )

        battery = (
            battery_model.predict(X)[0]
        )

        generation = (
            generation_model.predict(X)[0]
        )

        result.append({

            "date":
            future_time.strftime("%d.%m"),

            "total_consumption":
            round(float(total), 2),

            "solar_consumption":
            round(float(solar), 2),

            "battery_consumption":
            round(float(battery), 2),

            "solar_generation":
            round(float(generation), 2)
        })

    return result


def generate_recommendations():

    forecast = forecast_24h()

    recommendations = []


    peak = max(
        forecast,
        key=lambda x:
        x["total_consumption"]
    )

    recommendations.append(

        f"Expected peak load at "
        f"{peak['time']} "
        f"({peak['total_consumption']} kWh)."
    )


    best_solar = max(
        forecast,
        key=lambda x:
        x["solar_generation"]
    )

    recommendations.append(

        f"Highest solar generation "
        f"expected at "
        f"{best_solar['time']} "
        f"({best_solar['solar_generation']} kWh)."
    )


    battery_peak = max(
        forecast,
        key=lambda x:
        x["battery_consumption"]
    )

    recommendations.append(

        f"Battery usage peak expected "
        f"at {battery_peak['time']}."
    )

    return recommendations