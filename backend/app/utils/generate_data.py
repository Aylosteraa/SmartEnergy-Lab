import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


START_DATE = "2025-02-19"
END_DATE = "2026-05-18"

FREQ = "10min"

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
df["minute"] = df["Datetime"].dt.minute

df["day_of_week"] = df["Datetime"].dt.dayofweek

df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)

# WEATHER FEATURES

# Температура
df["temp_dry"] = (
    10
    + 10 * np.sin(2 * np.pi * df["hour"] / 24)
    + np.random.normal(0, 2, len(df))
)

# Хмарність
df["cloudiness"] = np.clip(
    np.random.normal(50, 25, len(df)),
    0,
    100
)

# Вологість
df["humidity"] = np.clip(
    np.random.normal(60, 15, len(df)),
    20,
    100
)

# Вітер
df["wind_speed"] = np.clip(
    np.random.normal(5, 2, len(df)),
    0,
    20
)

# SOLAR GENERATION

solar_generation = []

for _, row in df.iterrows():

    hour = row["hour"]

    cloudiness = row["cloudiness"]

    # ніч
    if hour < 6 or hour > 20:

        generation = 0

    else:

        # денна крива
        solar_factor = np.sin(
            np.pi * (hour - 6) / 14
        )

        cloud_factor = 1 - (cloudiness / 100)

        generation = (
            solar_factor
            * cloud_factor
            * random.uniform(2, 6)
        )

    solar_generation.append(
        max(generation, 0)
    )

df["solar_generation"] = solar_generation


# TOTAL CONSUMPTION

consumption_total = []

for _, row in df.iterrows():

    base = random.uniform(1.5, 4)

    # вечірній пік
    if 18 <= row["hour"] <= 23:
        base += random.uniform(1, 3)

    # ранковий пік
    if 6 <= row["hour"] <= 9:
        base += random.uniform(0.5, 2)

    # вихідні
    if row["is_weekend"]:
        base += random.uniform(0.3, 1)

    consumption_total.append(base)

df["consumption_total"] = consumption_total


# ENERGY SOURCE STATES

states = []

current_state = "grid"

remaining_steps = 0

possible_states = [
    "grid",
    "solar",
    "hybrid",
    "battery"
]

for _, row in df.iterrows():

    if remaining_steps <= 0:

        hour = row["hour"]

        solar = row["solar_generation"]

        # =====================================
        # SMART STATE LOGIC
        # =====================================

        if solar > 3:

            current_state = random.choices(
                ["solar", "hybrid"],
                weights=[0.7, 0.3]
            )[0]

        elif solar > 1:

            current_state = random.choices(
                ["hybrid", "grid"],
                weights=[0.6, 0.4]
            )[0]

        else:

            current_state = random.choices(
                ["grid", "battery"],
                weights=[0.8, 0.2]
            )[0]

        # =====================================
        # STATE DURATION
        # =====================================

        remaining_steps = random.randint(
            6,   # 1 година
            36   # 6 годин
        )

    states.append(current_state)

    remaining_steps -= 1

df["energy_source"] = states


# ENERGY FLOW SPLIT

grid_usage = []
solar_usage = []
battery_usage = []

for _, row in df.iterrows():

    total = row["consumption_total"]

    solar_gen = row["solar_generation"]

    state = row["energy_source"]

    grid = 0
    solar = 0
    battery = 0

    # =====================================
    # GRID
    # =====================================

    if state == "grid":

        grid = total

    # =====================================
    # SOLAR
    # =====================================

    elif state == "solar":

        solar = min(total, solar_gen)

        grid = max(total - solar, 0)

    # =====================================
    # HYBRID
    # =====================================

    elif state == "hybrid":

        solar = min(
            total * random.uniform(0.4, 0.8),
            solar_gen
        )

        grid = total - solar

    # =====================================
    # BATTERY
    # =====================================

    elif state == "battery":

        battery = total * random.uniform(0.5, 1)

        grid = total - battery

    grid_usage.append(grid)

    solar_usage.append(solar)

    battery_usage.append(battery)

df["consumption_grid"] = grid_usage

df["consumption_solar"] = solar_usage

df["consumption_battery"] = battery_usage


# BATTERY LEVEL

battery_levels = []

battery_level = 70

for _, row in df.iterrows():

    battery_level += (
        row["solar_generation"] * 0.3
    )

    battery_level -= (
        row["consumption_battery"] * 0.5
    )

    battery_level = np.clip(
        battery_level,
        0,
        100
    )

    battery_levels.append(
        battery_level
    )

df["battery_level"] = battery_levels

# LAG FEATURES

df = df.sort_values("Datetime")

df["lag_24h"] = (
    df["consumption_total"]
    .shift(24 * 6)
)

df["rolling_24h"] = (
    df["consumption_total"]
    .rolling(24 * 6)
    .mean()
)

# SAVE

df.to_csv(
    "app/data/generated_energy_data.csv",
    index=False
)

print(df.head())

print("\nDataset generated successfully.")