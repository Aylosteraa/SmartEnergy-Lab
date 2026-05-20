# energy_simulator.py

import json
import math
import random
import time

import paho.mqtt.publish as publish


BROKER = "localhost"

PORT = 1883

TOPICS = {

    "solar": "smartenergy/solar",

    "battery": "smartenergy/battery",

    "load": "smartenergy/load",

    "meter": "smartenergy/meter"
}


battery_soc = 65.0

solar_energy_today = 0

grid_energy_today = 0


while True:

    current_time = time.localtime()

    hour = current_time.tm_hour

    minute = current_time.tm_min

    if 6 <= hour <= 18:

        base_solar = (
            500 *
            math.sin(
                math.pi * (hour - 6) / 12
            )
        )

        solar_power = max(
            0,
            base_solar + random.randint(-30, 30)
        )

    else:

        solar_power = 0

    solar_power = round(solar_power, 2)

    # ACS712 measures current

    solar_voltage = round(
        random.uniform(17.0, 22.0),
        2
    )

    solar_current = round(
        solar_power / solar_voltage
        if solar_voltage > 0 else 0,
        2
    )


    # House consumption simulation

    if 18 <= hour <= 23:

        # evening peak

        load_power = random.randint(350, 700)

    elif 0 <= hour <= 5:

        # night low usage

        load_power = random.randint(80, 180)

    else:

        load_power = random.randint(150, 450)

    load_voltage = round(
        random.uniform(220, 235),
        2
    )

    load_current = round(
        load_power / load_voltage,
        2
    )

    battery_power = 0

    grid_power = 0



    if solar_power >= load_power:

        excess = solar_power - load_power

        # charge battery

        if battery_soc < 100:

            battery_power = -excess

            battery_soc += excess / 1000


    else:

        deficit = load_power - solar_power

        # battery helps

        if battery_soc > 20:

            battery_power = deficit

            battery_soc -= deficit / 1200

        else:

            # take from grid

            grid_power = deficit

    battery_soc = round(
        max(0, min(100, battery_soc)),
        1
    )

    battery_voltage = round(
        random.uniform(11.8, 13.0),
        2
    )

    battery_current = round(
        battery_power / battery_voltage
        if battery_voltage > 0 else 0,
        2
    )

    grid_voltage = round(
        random.uniform(220, 235),
        2
    )

    grid_current = round(
        grid_power / grid_voltage
        if grid_voltage > 0 else 0,
        2
    )

    solar_energy_today += solar_power * (5 / 3600)

    grid_energy_today += grid_power * (5 / 3600)


    # ACS712

    solar_payload = {

        "sensor": "ACS712",

        "voltage": solar_voltage,

        "current": solar_current,

        "power": solar_power,

        "energy_today_wh": round(
            solar_energy_today,
            2
        )
    }

    # INA226

    battery_payload = {

        "sensor": "INA226",

        "voltage": battery_voltage,

        "current": battery_current,

        "power": round(
            battery_power,
            2
        ),

        "soc": battery_soc
    }

    # SCT-013

    load_payload = {

        "sensor": "SCT-013",

        "load_voltage": load_voltage,

        "load_current": load_current,

        "load_power": load_power
    }

    # SMART METER

    meter_payload = {

        "sensor": "SMART_METER",

        "grid_voltage": grid_voltage,

        "grid_current": grid_current,

        "grid_power": round(
            grid_power,
            2
        ),

        "grid_energy_today_kwh": round(
            grid_energy_today / 1000,
            3
        )
    }


    publish.single(
        TOPICS["solar"],
        json.dumps(solar_payload),
        hostname=BROKER,
        port=PORT
    )

    publish.single(
        TOPICS["battery"],
        json.dumps(battery_payload),
        hostname=BROKER,
        port=PORT
    )

    publish.single(
        TOPICS["load"],
        json.dumps(load_payload),
        hostname=BROKER,
        port=PORT
    )

    publish.single(
        TOPICS["meter"],
        json.dumps(meter_payload),
        hostname=BROKER,
        port=PORT
    )
