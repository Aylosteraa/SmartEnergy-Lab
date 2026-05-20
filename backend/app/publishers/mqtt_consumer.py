import json
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from app.db.database import SessionLocal

from app.db.models import (
    ElectricityMeterReading,
    SolarSystemReading
)

from app.publishers.realtime_cache import latest_realtime_data


# MQTT CONFIG

BROKER = "localhost"

PORT = 1883

TOPICS = [

    ("smartenergy/solar", 0),

    ("smartenergy/battery", 0),

    ("smartenergy/load", 0),

    ("smartenergy/meter", 0)
]


# DATABASE

db = SessionLocal()

# MQTT CALLBACK

def on_connect(client, userdata, flags, rc):

    print("Connected to MQTT Broker")

    client.subscribe(TOPICS)


def on_message(client, userdata, msg):

    payload = json.loads(
        msg.payload.decode()
    )

    topic = msg.topic

    print(f"\nTOPIC: {topic}")

    print(payload)

    # -----------------------------------------

    if topic == "smartenergy/solar":

        latest_realtime_data["solar"] = payload

    elif topic == "smartenergy/battery":

        latest_realtime_data["battery"] = payload

    elif topic == "smartenergy/load":

        latest_realtime_data["load"] = payload

    elif topic == "smartenergy/meter":

        latest_realtime_data["meter"] = payload


# MQTT CLIENT

client = mqtt.Client()

client.on_connect = on_connect

client.on_message = on_message

client.connect(BROKER, PORT, 60)

client.loop_start()


# SAVE TO DATABASE EVERY 10 MINUTES

while True:

    print("\nWaiting 10 minutes...\n")

    time.sleep(600)

    try:

        solar = latest_realtime_data["solar"]

        battery = latest_realtime_data["battery"]

        load = latest_realtime_data["load"]

        meter = latest_realtime_data["meter"]

        # CALCULATIONS

        solar_generation = solar.get(
            "power",
            0
        )

        battery_level = battery.get(
            "soc",
            0
        )

        consumption_grid = meter.get(
            "grid_power",
            0
        )

        consumption_total = load.get(
            "load_power",
            0
        )

        battery_power = battery.get(
            "power",
            0
        )


        if battery_power > 0:

            consumption_battery = battery_power

        else:

            consumption_battery = 0

     

        consumption_solar = max(
            0,
            consumption_total
            - consumption_grid
            - consumption_battery
        )


        temp_dry = 24

        cloudiness = 30

        humidity = 60

        wind_speed = 3


        solar_reading = SolarSystemReading(

            solar_system_id=1,

            solar_generation=solar_generation,

            battery_level=battery_level,

            temp_dry=temp_dry,

            cloudiness=cloudiness,

            humidity=humidity,

            wind_speed=wind_speed,

            timestamp=datetime.utcnow()
        )

        db.add(solar_reading)


        meter_reading = ElectricityMeterReading(

            electricity_meter_id=1,

            consumption_total=consumption_total,

            consumption_grid=consumption_grid,

            consumption_solar=consumption_solar,

            consumption_battery=consumption_battery,

            temp_dry=temp_dry,

            cloudiness=cloudiness,

            humidity=humidity,

            wind_speed=wind_speed,

            timestamp=datetime.utcnow()
        )

        db.add(meter_reading)

        db.commit()

        print("\nSaved to database successfully")

    except Exception as e:

        print("\nDATABASE ERROR")

        print(str(e))

        db.rollback()