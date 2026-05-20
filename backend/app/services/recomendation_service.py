from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models import Notification


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    level: str = "info"
):

    notification = Notification(

        user_id=user_id,

        title=title,

        message=message,

        level=level
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)

    return notification


def get_tariff_period(hour: int):

    # night tariff

    if hour >= 23 or hour < 7:

        return "night"

    # peak load

    elif 18 <= hour <= 22:

        return "peak"

    # daytime

    else:

        return "day"


def generate_energy_recommendations(

    db: Session,

    user_id: int,

    realtime_data: dict
):

    solar = realtime_data.get(
        "solar",
        {}
    )

    battery = realtime_data.get(
        "battery",
        {}
    )

    load = realtime_data.get(
        "load",
        {}
    )

    meter = realtime_data.get(
        "meter",
        {}
    )

    solar_power = solar.get(
        "power",
        0
    )

    battery_soc = battery.get(
        "soc",
        0
    )

    battery_power = battery.get(
        "power",
        0
    )

    load_power = load.get(
        "load_power",
        0
    )

    grid_power = meter.get(
        "grid_power",
        0
    )

    now = datetime.now()

    current_hour = now.hour

    tariff_period = get_tariff_period(
        current_hour
    )

    if solar_power > 400:

        create_notification(

            db=db,

            user_id=user_id,

            title="Висока сонячна генерація",

            message=(
                "Зараз система виробляє "
                "велику кількість сонячної енергії. "
                "Рекомендується використовувати "
                "енергоємні прилади: "
                "бойлер, пральну машину, "
                "кондиціонер або зарядку "
                "електромобіля."
            ),

            level="success"
        )

    elif solar_power < 100:

        create_notification(

            db=db,

            user_id=user_id,

            title="Низька сонячна генерація",

            message=(
                "Рівень генерації сонячної "
                "енергії низький. "
                "Рекомендується зменшити "
                "навантаження або перейти "
                "на використання акумулятора."
            ),

            level="warning"
        )

    if battery_soc < 20:

        create_notification(

            db=db,

            user_id=user_id,

            title="Низький заряд акумулятора",

            message=(
                "Рівень заряду акумулятора "
                "критично низький. "
                "Рекомендується зарядити "
                "акумулятор у денний період "
                "при високій сонячній генерації."
            ),

            level="danger"
        )

    elif battery_soc > 90:

        create_notification(

            db=db,

            user_id=user_id,

            title="Акумулятор заряджено",

            message=(
                "Акумулятор майже повністю "
                "заряджений. "
                "Система готова до "
                "автономного живлення."
            ),

            level="success"
        )

    if battery_power < 0:

        create_notification(

            db=db,

            user_id=user_id,

            title="Заряджання акумулятора",

            message=(
                "Акумулятор заряджається "
                "надлишковою сонячною енергією."
            ),

            level="info"
        )

    if battery_power > 0:

        create_notification(

            db=db,

            user_id=user_id,

            title="Живлення від акумулятора",

            message=(
                "Система використовує "
                "акумулятор для живлення "
                "будинку та зменшення "
                "споживання з мережі."
            ),

            level="info"
        )

    if grid_power > 350:

        create_notification(

            db=db,

            user_id=user_id,

            title="Високе споживання з мережі",

            message=(
                "Будинок активно споживає "
                "електроенергію із загальної "
                "мережі. "
                "Рекомендується перейти "
                "на сонячну енергію "
                "або використання акумулятора."
            ),

            level="warning"
        )


    if tariff_period == "peak":

        create_notification(

            db=db,

            user_id=user_id,

            title="Пікове навантаження",

            message=(
                "Зараз піковий період "
                "споживання електроенергії "
                "(18:00–22:00). "
                "Рекомендується обмежити "
                "використання енергоємних "
                "пристроїв."
            ),

            level="danger"
        )

    elif tariff_period == "night":

        create_notification(

            db=db,

            user_id=user_id,

            title="Нічний тариф",

            message=(
                "Зараз діє нічний тариф "
                "на електроенергію. "
                "Оптимальний час для "
                "заряджання акумуляторів "
                "та використання "
                "енергоємних приладів."
            ),

            level="success"
        )

    if 10 <= current_hour <= 16:

        create_notification(

            db=db,

            user_id=user_id,

            title="Оптимальний час сонячної генерації",

            message=(
                "Денний період забезпечує "
                "максимальну ефективність "
                "сонячних панелей. "
                "Рекомендується використовувати "
                "електроприлади саме зараз."
            ),

            level="success"
        )

    if load_power > 600:

        create_notification(

            db=db,

            user_id=user_id,

            title="Високе навантаження",

            message=(
                "Зафіксовано високе "
                "енергоспоживання будинку. "
                "Рекомендується вимкнути "
                "частину приладів або "
                "перейти на живлення "
                "від акумулятора."
            ),

            level="warning"
        )

    elif load_power < 150:

        create_notification(

            db=db,

            user_id=user_id,

            title="Низьке енергоспоживання",

            message=(
                "Поточне навантаження "
                "системи низьке. "
                "Це сприятливий час "
                "для заряджання акумулятора."
            ),

            level="info"
        )

    if grid_power == 0 and solar_power > 250:

        create_notification(

            db=db,

            user_id=user_id,

            title="Автономне живлення",

            message=(
                "Будинок повністю "
                "живиться від сонячної "
                "енергії без використання "
                "загальної електромережі."
            ),

            level="success"
        )