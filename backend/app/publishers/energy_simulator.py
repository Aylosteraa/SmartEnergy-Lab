import json
import math
import random
import time

import paho.mqtt.publish as publish


# =========================================================
# MQTT
# =========================================================

BROKER = "localhost"

PORT = 1883

TOPICS = {

    "solar":
        "smartenergy/solar",

    "battery":
        "smartenergy/battery",

    "load":
        "smartenergy/load",

    "meter":
        "smartenergy/meter"
}


# =========================================================
# SOLAR PANELS
# =========================================================

TOTAL_PANELS = 2

POWER_PER_PANEL = 500

ACTIVE_PANELS = 2


# =========================================================
# BATTERY
# =========================================================

battery_soc = 65.0


# =========================================================
# ENERGY COUNTERS
# =========================================================

solar_energy_today = 0

grid_energy_today = 0


# =========================================================
# SIMULATION
# =========================================================

while True:

    current_time = time.localtime()

    hour = current_time.tm_hour

    minute = current_time.tm_min

    # =====================================================
    # SOLAR GENERATION
    # =====================================================

    if 6 <= hour <= 18:

        solar_per_panel = (

            POWER_PER_PANEL
            * math.sin(
                math.pi
                * (hour - 6)
                / 12
            )
        )

        solar_power = (

            solar_per_panel
            * ACTIVE_PANELS

        )

        solar_power += random.randint(
            -30,
            30
        )

        solar_power = max(
            0,
            solar_power
        )

    else:

        solar_power = 0


    solar_power = round(
        solar_power,
        2
    )


    # =====================================================
    # SOLAR VOLTAGE / CURRENT
    # =====================================================

    solar_voltage = round(
        random.uniform(
            17.0,
            22.0
        ),
        2
    )

    solar_current = round(

        solar_power
        / solar_voltage

        if solar_voltage > 0
        else 0,

        2
    )


    # =====================================================
    # HOUSE CONSUMPTION
    # =====================================================

    if 18 <= hour <= 23:

        load_power = random.randint(
            350,
            700
        )

    elif 0 <= hour <= 5:

        load_power = random.randint(
            80,
            180
        )

    else:

        load_power = random.randint(
            150,
            450
        )


    load_voltage = round(

        random.uniform(
            220,
            235
        ),

        2
    )


    load_current = round(

        load_power
        / load_voltage,

        2
    )


    # =====================================================
    # ENERGY BALANCE
    # =====================================================

    battery_power = 0

    grid_power = 0


    if solar_power >= load_power:

        excess = (
            solar_power
            - load_power
        )

        # -----------------------------------------------
        # CHARGE BATTERY
        # -----------------------------------------------

        if battery_soc < 100:

            battery_power = -excess

            battery_soc += (
                excess
                / 1000
            )

        else:

            # Battery full.
            # Excess energy remains available
            # for high-load scenarios.
            battery_power = 0

    else:

        deficit = (
            load_power
            - solar_power
        )

        # -----------------------------------------------
        # BATTERY HELPS
        # -----------------------------------------------

        if battery_soc > 20:

            battery_power = deficit

            battery_soc -= (
                deficit
                / 1200
            )

        else:

            # -------------------------------------------
            # GRID
            # -------------------------------------------

            grid_power = deficit


    battery_soc = round(

        max(
            0,
            min(
                100,
                battery_soc
            )
        ),

        1
    )


    # =====================================================
    # BATTERY
    # =====================================================

    battery_voltage = round(

        random.uniform(
            11.8,
            13.0
        ),

        2
    )


    battery_current = round(

        battery_power
        / battery_voltage

        if battery_voltage > 0
        else 0,

        2
    )


    # =====================================================
    # GRID
    # =====================================================

    grid_voltage = round(

        random.uniform(
            220,
            235
        ),

        2
    )


    grid_current = round(

        grid_power
        / grid_voltage

        if grid_voltage > 0
        else 0,

        2
    )


    # =====================================================
    # ENERGY
    # =====================================================

    solar_energy_today += (
        solar_power
        * (5 / 3600)
    )

    grid_energy_today += (
        grid_power
        * (5 / 3600)
    )


    # =====================================================
    # SOLAR PAYLOAD
    # =====================================================

    solar_payload = {

        "sensor":
            "ACS712",

        "voltage":
            solar_voltage,

        "current":
            solar_current,

        "power":
            solar_power,

        "panels":
            ACTIVE_PANELS,

        "total_panels":
            TOTAL_PANELS,

        "power_per_panel":
            POWER_PER_PANEL,

        "energy_today_wh":
            round(
                solar_energy_today,
                2
            )
    }


    # =====================================================
    # BATTERY PAYLOAD
    # =====================================================

    battery_payload = {

        "sensor":
            "INA226",

        "voltage":
            battery_voltage,

        "current":
            battery_current,

        "power":
            round(
                battery_power,
                2
            ),

        "soc":
            battery_soc
    }


    # =====================================================
    # LOAD PAYLOAD
    # =====================================================

    load_payload = {

        "sensor":
            "SCT-013",

        "load_voltage":
            load_voltage,

        "load_current":
            load_current,

        "load_power":
            load_power
    }


    # =====================================================
    # SMART METER
    # =====================================================

    meter_payload = {

        "sensor":
            "SMART_METER",

        "grid_voltage":
            grid_voltage,

        "grid_current":
            grid_current,

        "grid_power":
            round(
                grid_power,
                2
            ),

        "grid_energy_today_kwh":
            round(
                grid_energy_today / 1000,
                3
            )
    }


    # =====================================================
    # MQTT PUBLISH
    # =====================================================

    publish.single(

        TOPICS["solar"],

        json.dumps(
            solar_payload
        ),

        hostname=BROKER,

        port=PORT
    )


    publish.single(

        TOPICS["battery"],

        json.dumps(
            battery_payload
        ),

        hostname=BROKER,

        port=PORT
    )


    publish.single(

        TOPICS["load"],

        json.dumps(
            load_payload
        ),

        hostname=BROKER,

        port=PORT
    )


    publish.single(

        TOPICS["meter"],

        json.dumps(
            meter_payload
        ),

        hostname=BROKER,

        port=PORT
    )


    # =====================================================
    # NEXT ITERATION
    # =====================================================

    time.sleep(5)