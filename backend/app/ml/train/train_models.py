import pandas as pd

from sklearn.ensemble import (
    RandomForestRegressor
)

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    mean_squared_error
)

import numpy as np

import joblib


def train_random_forest_model(

    csv_path: str,

    target: str,

    model_save_path: str
):


    df = pd.read_csv(csv_path)

    df["Datetime"] = pd.to_datetime(
        df["Datetime"]
    )

    features = [

        "month",
        "day",
        "hour",
        "day_of_week",
        "is_weekend",

        "temp_dry",
        "cloudiness",
        "humidity",
        "wind_speed",

        "lag_24h",
        "rolling_24h"
    ]

    df = df.dropna(
        subset=features + [target]
    )

    X = df[features]

    y = df[target]

    X_train, X_test, y_train, y_test = (

        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )
    )

    model = RandomForestRegressor(

        n_estimators=100,

        max_depth=10,

        random_state=42,

        n_jobs=-1
    )


    model.fit(
        X_train,
        y_train
    )


    y_pred = model.predict(
        X_test
    )


    rmse = np.sqrt(

        mean_squared_error(
            y_test,
            y_pred
        )
    )

    print(
        f"{target} RMSE: {rmse}"
    )

    joblib.dump(
        model,
        model_save_path
    )

    print(
        f"Model saved: {model_save_path}"
    )

    return model

train_random_forest_model(

    csv_path=
    "app/data/generated_energy_data.csv",

    target=
    "consumption_total",

    model_save_path=
    "app/ml/models/total_model.pkl"
)


train_random_forest_model(

    csv_path=
    "app/data/generated_energy_data.csv",

    target=
    "consumption_solar",

    model_save_path=
    "app/ml/models/solar_model.pkl"
)

train_random_forest_model(

    csv_path=
    "app/data/generated_energy_data.csv",

    target=
    "consumption_battery",

    model_save_path=
    "app/ml/models/battery_model.pkl"
)


train_random_forest_model(

    csv_path=
    "app/data/generated_energy_data.csv",

    target=
    "solar_generation",

    model_save_path=
    "app/ml/models/generation_model.pkl"
)