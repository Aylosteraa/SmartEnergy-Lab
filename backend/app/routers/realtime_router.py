import asyncio
import json
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.db.database import SessionLocal
from app.db.models import ElectricityMeterReading, SolarSystemReading
from app.publishers.realtime_cache import latest_realtime_data
from app.services.recomendation_service import generate_energy_recommendations

import os

router = APIRouter()

BROKER = os.getenv(
    "MQTT_BROKER",
    "localhost"
)

PORT = int(
    os.getenv(
        "MQTT_PORT",
        1883
    )
)

TOPICS = [

    ("smartenergy/solar", 0),

    ("smartenergy/battery", 0),

    ("smartenergy/load", 0),

    ("smartenergy/meter", 0)
]

last_notification_time = None

def on_connect(client, userdata, flags, rc):

    print("MQTT CONNECTED")

    client.subscribe(TOPICS)


def on_message(client, userdata, msg):

    payload = json.loads(
        msg.payload.decode()
    )

    topic = msg.topic

    print(f"\nTOPIC: {topic}")

    print(payload)

    if topic == "smartenergy/solar":

        latest_realtime_data["solar"] = payload

    elif topic == "smartenergy/battery":

        latest_realtime_data["battery"] = payload

    elif topic == "smartenergy/load":

        latest_realtime_data["load"] = payload

    elif topic == "smartenergy/meter":

        latest_realtime_data["meter"] = payload


mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect

mqtt_client.on_message = on_message

mqtt_started = False


async def save_to_db():

    while True:

        print("WAITING 10 MINUTES")

        await asyncio.sleep(600)

        db = SessionLocal()

        try:

            solar = latest_realtime_data["solar"]

            battery = latest_realtime_data["battery"]

            load = latest_realtime_data["load"]

            meter = latest_realtime_data["meter"]

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

            print("SAVED TO DATABASE")

            global last_notification_time

            now = datetime.utcnow()

            if (

                last_notification_time is None

                or

                now - last_notification_time
                >= timedelta(hours=3)
            ):

                generate_energy_recommendations(

                    db=db,

                    user_id=1,

                    realtime_data=latest_realtime_data
                )

                last_notification_time = now

                print("NOTIFICATIONS GENERATED")

        except Exception as e:

            print("DATABASE ERROR")

            print(str(e))

            db.rollback()

        finally:

            db.close()


db_task_started = False



@router.websocket("/realtime/ws")
async def websocket_endpoint(websocket: WebSocket):

    global mqtt_started

    global db_task_started

    print("WEBSOCKET ROUTE CALLED")

    await websocket.accept()

    print("WEBSOCKET CONNECTED")


    if not mqtt_started:

        mqtt_client.connect(
            BROKER,
            PORT,
            60
        )

        mqtt_client.loop_start()

        mqtt_started = True

        print("MQTT STARTED")

    if not db_task_started:

        asyncio.create_task(
            save_to_db()
        )

        db_task_started = True

        print("DB TASK STARTED")


    try:

        while True:

            try:

                data = json.dumps(

                    latest_realtime_data,

                    default=str
                )

                print(data)

                await websocket.send_text(data)

            except Exception as e:

                print("SEND ERROR")

                print(str(e))

            await asyncio.sleep(2)

    except WebSocketDisconnect:

        print("WEBSOCKET DISCONNECTED")

    except Exception as e:

        print("WEBSOCKET ERROR")

        print(str(e))