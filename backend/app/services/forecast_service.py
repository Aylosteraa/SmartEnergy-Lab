from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd


# =========================================================
# ML MODELS
# =========================================================

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


# =========================================================
# DETERMINISTIC RANDOM GENERATOR
# =========================================================

def get_stable_rng(dt: datetime):

    seed = (
        dt.year * 1000000
        + dt.month * 10000
        + dt.day * 100
        + dt.hour
    )

    return np.random.default_rng(seed)


# =========================================================
# WEATHER FEATURES
# =========================================================

def generate_weather_features(dt: datetime):

    hour = dt.hour

    rng = get_stable_rng(dt)

    temp = (
        15
        + 10 * np.sin(
            2 * np.pi * hour / 24
        )
        + rng.normal(0, 1)
    )

    cloudiness = np.clip(

        50
        + 20 * np.sin(
            2 * np.pi * hour / 24
        )
        + rng.normal(0, 10),

        0,
        100
    )

    humidity = np.clip(

        60
        + rng.normal(0, 5),

        20,
        100
    )

    wind_speed = np.clip(

        5
        + rng.normal(0, 1),

        0,
        20
    )

    return {

        "temp_dry":
            float(temp),

        "cloudiness":
            float(cloudiness),

        "humidity":
            float(humidity),

        "wind_speed":
            float(wind_speed)
    }


# =========================================================
# FEATURES
# =========================================================

def create_features(dt: datetime):

    weather = generate_weather_features(
        dt
    )

    rng = get_stable_rng(dt)

    features = {

        "month":
            dt.month,

        "day":
            dt.day,

        "hour":
            dt.hour,

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

        "lag_24h":
            float(
                rng.uniform(2, 5)
            ),

        "rolling_24h":
            float(
                rng.uniform(2, 5)
            )
    }

    return pd.DataFrame(
        [features]
    )


# =========================================================
# FORECAST 24H
# =========================================================

def forecast_24h():

    now = datetime.now()

    result = []

    for i in range(24):

        future_time = (
            now
            + timedelta(hours=i)
        )

        X = create_features(
            future_time
        )

        total = float(
            total_model.predict(X)[0]
        )

        solar = float(
            solar_model.predict(X)[0]
        )

        battery = float(
            battery_model.predict(X)[0]
        )

        generation = float(
            generation_model.predict(X)[0]
        )

        # Не допускаємо дивних від'ємних значень
        total = max(
            0,
            total
        )

        solar = max(
            0,
            solar
        )

        generation = max(
            0,
            generation
        )

        balance = (
            generation
            - total
        )

        result.append({

            "time":
                future_time.strftime(
                    "%H:%M"
                ),

            "total_consumption":
                round(total, 2),

            "solar_consumption":
                round(solar, 2),

            "battery_consumption":
                round(battery, 2),

            "solar_generation":
                round(generation, 2),

            "energy_balance":
                round(balance, 2)
        })

    return result


# =========================================================
# FORECAST 7 DAYS
# =========================================================

def forecast_7d():

    now = datetime.now()

    result = []

    for i in range(7):

        future_time = (
            now
            + timedelta(days=i)
        ).replace(
            hour=13,
            minute=0,
            second=0,
            microsecond=0
        )

        X = create_features(
            future_time
        )

        total = float(
            total_model.predict(X)[0]
        )

        solar = float(
            solar_model.predict(X)[0]
        )

        battery = float(
            battery_model.predict(X)[0]
        )

        generation = float(
            generation_model.predict(X)[0]
        )

        total = max(
            0,
            total
        )

        solar = max(
            0,
            solar
        )

        generation = max(
            0,
            generation
        )

        result.append({

            "date":
                future_time.strftime(
                    "%Y-%m-%d"
                ),

            "total_consumption":
                round(total, 2),

            "solar_consumption":
                round(solar, 2),

            "battery_consumption":
                round(battery, 2),

            "solar_generation":
                round(generation, 2),

            "energy_balance":
                round(
                    generation - total,
                    2
                )
        })

    return result


# =========================================================
# FORECAST MONTH
# =========================================================

def forecast_month():

    now = datetime.now()

    result = []

    for i in range(30):

        future_time = (
            now
            + timedelta(days=i)
        ).replace(
            hour=13,
            minute=0,
            second=0,
            microsecond=0
        )

        X = create_features(
            future_time
        )

        total = float(
            total_model.predict(X)[0]
        )

        solar = float(
            solar_model.predict(X)[0]
        )

        battery = float(
            battery_model.predict(X)[0]
        )

        generation = float(
            generation_model.predict(X)[0]
        )

        total = max(
            0,
            total
        )

        solar = max(
            0,
            solar
        )

        generation = max(
            0,
            generation
        )

        result.append({

            "date":
                future_time.strftime(
                    "%d.%m"
                ),

            "total_consumption":
                round(total, 2),

            "solar_consumption":
                round(solar, 2),

            "battery_consumption":
                round(battery, 2),

            "solar_generation":
                round(generation, 2),

            "energy_balance":
                round(
                    generation - total,
                    2
                )
        })

    return result