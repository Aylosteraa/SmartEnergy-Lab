import asyncio
import json
import os
from datetime import datetime

import paho.mqtt.client as mqtt

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.db.database import SessionLocal
from app.db.models import ElectricityMeterReading, SolarSystemReading
from app.publishers.realtime_cache import latest_realtime_data

from app.services.recomendation_service import (
    create_notification,
    get_critical_recommendation
)


router = APIRouter()


# =========================================================
# MQTT
# =========================================================

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


# =========================================================
# GLOBAL STATE
# =========================================================

mqtt_started = False

db_task_started = False


# ---------------------------------------------------------
# Стан критичного сповіщення
# ---------------------------------------------------------
#
# Наприклад:
#
# None
#   ↓
# critical_battery
#
# Поки стан залишається critical_battery,
# нові однакові Notification не створюються.
#

critical_state_key = None


# Захист від одночасної обробки
critical_notification_lock = asyncio.Lock()


# =========================================================
# MQTT CALLBACKS
# =========================================================

def on_connect(
    client,
    userdata,
    flags,
    rc
):

    print("MQTT CONNECTED")

    client.subscribe(TOPICS)


def on_message(
    client,
    userdata,
    msg
):

    try:

        payload = json.loads(
            msg.payload.decode()
        )

        topic = msg.topic

        print(
            f"\nTOPIC: {topic}"
        )

        print(payload)


        if topic == "smartenergy/solar":

            latest_realtime_data[
                "solar"
            ] = payload


        elif topic == "smartenergy/battery":

            latest_realtime_data[
                "battery"
            ] = payload


        elif topic == "smartenergy/load":

            latest_realtime_data[
                "load"
            ] = payload


        elif topic == "smartenergy/meter":

            latest_realtime_data[
                "meter"
            ] = payload


    except Exception as e:

        print(
            "MQTT MESSAGE ERROR"
        )

        print(str(e))


# =========================================================
# MQTT CLIENT
# =========================================================

mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect

mqtt_client.on_message = on_message


# =========================================================
# SAVE REALTIME DATA TO DATABASE
# =========================================================

async def save_to_db():

    while True:

        print(
            "WAITING 10 MINUTES"
        )

        await asyncio.sleep(600)


        db = SessionLocal()


        try:

            solar = (
                latest_realtime_data[
                    "solar"
                ]
            )

            battery = (
                latest_realtime_data[
                    "battery"
                ]
            )

            load = (
                latest_realtime_data[
                    "load"
                ]
            )

            meter = (
                latest_realtime_data[
                    "meter"
                ]
            )


            # =================================================
            # CURRENT VALUES
            # =================================================

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


            # =================================================
            # BATTERY CONSUMPTION
            # =================================================

            if battery_power > 0:

                consumption_battery = (
                    battery_power
                )

            else:

                consumption_battery = 0


            # =================================================
            # SOLAR CONSUMPTION
            # =================================================

            consumption_solar = max(

                0,

                consumption_total
                - consumption_grid
                - consumption_battery

            )


            # =================================================
            # WEATHER DATA
            # =================================================

            temp_dry = 24

            cloudiness = 30

            humidity = 60

            wind_speed = 3


            # =================================================
            # SOLAR SYSTEM READING
            # =================================================

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


            db.add(
                solar_reading
            )


            # =================================================
            # ELECTRICITY METER READING
            # =================================================

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


            db.add(
                meter_reading
            )


            # =================================================
            # COMMIT
            # =================================================

            db.commit()


            print(
                "SAVED TO DATABASE"
            )


        except Exception as e:

            print(
                "DATABASE ERROR"
            )

            print(
                str(e)
            )


            db.rollback()


        finally:

            db.close()


# =========================================================
# CHECK CRITICAL NOTIFICATION
# =========================================================

async def check_critical_notification():

    global critical_state_key


    # -----------------------------------------------------
    # Отримуємо поточну критичну рекомендацію
    # -----------------------------------------------------

    critical = (
        get_critical_recommendation(
            latest_realtime_data
        )
    )


    async with critical_notification_lock:


        # =================================================
        # КРИТИЧНОГО СТАНУ НЕМАЄ
        # =================================================

        if critical is None:

            # Скидаємо стан.
            #
            # Це дозволить створити нове
            # повідомлення, якщо система
            # знову увійде в критичний стан.

            critical_state_key = None

            return None


        # =================================================
        # КЛЮЧ КРИТИЧНОГО СТАНУ
        # =================================================

        current_key = critical.get(
            "critical_key"
        )


        # =================================================
        # КРИТИЧНИЙ СТАН ВЖЕ ОБРОБЛЕНО
        # =================================================

        if (
            current_key ==
            critical_state_key
        ):

            return None


        # =================================================
        # НОВИЙ КРИТИЧНИЙ СТАН
        # =================================================

        db = SessionLocal()


        try:

            notification = create_notification(

                db=db,

                user_id=1,

                title=critical[
                    "title"
                ],

                message=critical[
                    "message"
                ],

                level=critical[
                    "level"
                ]

            )


            # -------------------------------------------------
            # Запам'ятовуємо стан
            # -------------------------------------------------

            critical_state_key = (
                current_key
            )


            print(
                "CRITICAL NOTIFICATION CREATED"
            )

            print(
                critical[
                    "title"
                ]
            )


            # -------------------------------------------------
            # Дані для WebSocket
            # -------------------------------------------------

            return {

                "id": notification.id,

                "title": notification.title,

                "message": notification.message,

                "level": notification.level,

                "created_at": (

                    notification.created_at.isoformat()

                    if notification.created_at

                    else None

                )

            }


        except Exception as e:

            db.rollback()


            print(
                "CRITICAL NOTIFICATION ERROR"
            )

            print(
                str(e)
            )


            return None


        finally:

            db.close()


# =========================================================
# WEBSOCKET
# =========================================================

@router.websocket(
    "/realtime/ws"
)
async def websocket_endpoint(
    websocket: WebSocket
):

    global mqtt_started

    global db_task_started


    print(
        "WEBSOCKET ROUTE CALLED"
    )


    # =====================================================
    # ACCEPT
    # =====================================================

    await websocket.accept()


    print(
        "WEBSOCKET CONNECTED"
    )


    # =====================================================
    # START MQTT
    # =====================================================

    if not mqtt_started:

        try:

            mqtt_client.connect(

                BROKER,

                PORT,

                60

            )

            mqtt_client.loop_start()

            mqtt_started = True


            print(
                "MQTT STARTED"
            )


        except Exception as e:

            print(
                "MQTT CONNECTION ERROR"
            )

            print(
                str(e)
            )


    # =====================================================
    # START DATABASE TASK
    # =====================================================

    if not db_task_started:

        asyncio.create_task(
            save_to_db()
        )

        db_task_started = True


        print(
            "DB TASK STARTED"
        )


    # =====================================================
    # WEBSOCKET LOOP
    # =====================================================

    try:

        while True:

            try:

                # =========================================
                # CHECK CRITICAL NOTIFICATION
                # =========================================

                notification = (
                    await check_critical_notification()
                )


                # =========================================
                # CREATE RESPONSE
                # =========================================

                payload = dict(
                    latest_realtime_data
                )


                # =========================================
                # ADD NOTIFICATION ONLY
                # WHEN A NEW ONE APPEARED
                # =========================================

                if notification is not None:

                    payload[
                        "notification"
                    ] = notification


                # =========================================
                # SEND DATA
                # =========================================

                data = json.dumps(

                    payload,

                    default=str

                )


                print(
                    data
                )


                await websocket.send_text(
                    data
                )


            except Exception as e:

                print(
                    "SEND ERROR"
                )

                print(
                    str(e)
                )


            # =============================================
            # REALTIME UPDATE EVERY 2 SECONDS
            # =============================================

            await asyncio.sleep(2)


    except WebSocketDisconnect:

        print(
            "WEBSOCKET DISCONNECTED"
        )


    except Exception as e:

        print(
            "WEBSOCKET ERROR"
        )

        print(
            str(e)
        )