import random
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Notification
from app.services.forecast_service import forecast_24h
from app.services.analytics_service import get_energy_analytics


# =========================================================
# НАЛАШТУВАННЯ
# =========================================================

SURPLUS_THRESHOLD = 50
HIGH_SURPLUS_THRESHOLD = 500

DEFICIT_THRESHOLD = -50
HIGH_DEFICIT_THRESHOLD = -400

LOW_BATTERY = 30
CRITICAL_BATTERY = 20
FULL_BATTERY = 95

HIGH_LOAD = 600


# =========================================================
# ТЕКСТИ РЕКОМЕНДАЦІЙ
# =========================================================

SURPLUS_BATTERY_MESSAGES = [
    (
        "Надлишок сонячної енергії",
        "Сонячна генерація перевищує поточне споживання "
        "на {balance:.0f} Вт. Рекомендується використати "
        "надлишок для заряджання акумулятора."
    ),
    (
        "Використайте сонячну енергію",
        "Зараз виробляється більше електроенергії, ніж "
        "споживається. Доступний надлишок становить "
        "{balance:.0f} Вт. Доцільно спрямувати його "
        "на заряджання акумулятора."
    ),
    (
        "Оптимальний час для накопичення енергії",
        "Поточна сонячна генерація дозволяє накопичувати "
        "надлишкову енергію. Заряд акумулятора становить "
        "{battery_soc:.0f}%. Рекомендується використати "
        "доступний надлишок для його заряджання."
    )
]


FULL_BATTERY_SURPLUS_MESSAGES = [
    (
        "Надлишок енергії",
        "Акумулятор заряджений на {battery_soc:.0f}%, "
        "а сонячна генерація перевищує споживання на "
        "{balance:.0f} Вт. Рекомендується зарядити "
        "електромобіль або виконати інше енергоємне завдання."
    ),
    (
        "Час використати надлишок",
        "Акумулятор майже повністю заряджений, тому "
        "додаткову сонячну енергію доцільно використати "
        "для бойлера, пральної машини, посудомийної машини "
        "або заряджання електромобіля."
    ),
    (
        "Висока доступність сонячної енергії",
        "Поточна генерація становить {solar_power:.0f} Вт, "
        "а споживання лише {load_power:.0f} Вт. "
        "Рекомендується перенести енергоємні завдання "
        "на поточний період, поки доступна сонячна енергія."
    )
]


CRITICAL_SURPLUS_MESSAGES = [
    (
        "Критичний надлишок генерації",
        "Сонячна генерація перевищує поточне споживання "
        "на {balance:.0f} Вт, а акумулятор заряджений на "
        "{battery_soc:.0f}%. Якщо додаткове споживання "
        "не потрібне, можна тимчасово відключити одну "
        "з сонячних панелей."
    ),
    (
        "Надмірна сонячна генерація",
        "Акумулятор повністю заряджений, а споживання "
        "залишається низьким. Рекомендується або підключити "
        "енергоємний прилад, або тимчасово відключити "
        "одну сонячну панель."
    ),
    (
        "Потрібно використати надлишок",
        "Доступний значний надлишок сонячної енергії "
        "({balance:.0f} Вт). Якщо електромобіль та інші "
        "енергоємні прилади не потребують заряджання, "
        "можна зменшити генерацію, відключивши одну панель."
    )
]


CURRENT_DEFICIT_MESSAGES = [
    (
        "Недостатня сонячна генерація",
        "Поточна генерація становить {solar_power:.0f} Вт, "
        "а споживання — {load_power:.0f} Вт. "
        "Рекомендується використати акумулятор для "
        "покриття поточного дефіциту."
    ),
    (
        "Дефіцит енергії",
        "Сонячної генерації зараз недостатньо для "
        "покриття навантаження. Заряд акумулятора "
        "становить {battery_soc:.0f}%, тому частину "
        "споживання можна покрити накопиченою енергією."
    ),
    (
        "Перехід на акумулятор",
        "Поточне навантаження перевищує сонячну генерацію "
        "на {deficit:.0f} Вт. За доступного заряду "
        "акумулятора рекомендується використати його "
        "для зменшення споживання електроенергії з мережі."
    )
]


LOW_BATTERY_MESSAGES = [
    (
        "Зберегти заряд акумулятора",
        "Дефіцит енергії становить {deficit:.0f} Вт, "
        "а заряд акумулятора лише {battery_soc:.0f}%. "
        "Рекомендується зменшити навантаження та "
        "не розряджати акумулятор нижче резервного рівня."
    ),
    (
        "Низький заряд акумулятора",
        "Акумулятор заряджений лише на {battery_soc:.0f}%, "
        "а сонячної генерації недостатньо. Рекомендується "
        "перенести необов'язкові енергоємні завдання "
        "на період вищої сонячної генерації."
    ),
    (
        "Обмежте споживання",
        "Через низький рівень заряду акумулятора "
        "({battery_soc:.0f}%) доцільно тимчасово "
        "зменшити використання потужних електроприладів."
    )
]


CRITICAL_BATTERY_MESSAGES = [
    (
        "Критично низький заряд",
        "Заряд акумулятора становить лише {battery_soc:.0f}%, "
        "а поточне споживання перевищує сонячну генерацію. "
        "Рекомендується перейти на мережу та не розряджати "
        "акумулятор нижче резервного рівня."
    ),
    (
        "Захист акумулятора",
        "Акумулятор майже розряджений ({battery_soc:.0f}%). "
        "Для збереження резерву рекомендується живити "
        "поточне навантаження від електромережі."
    )
]


IDLE_EMPTY_BATTERY_MESSAGES = [
    (
        "Зарядіть акумулятор",
        "Система не має поточного навантаження та сонячної "
        "генерації, а заряд акумулятора становить лише "
        "{battery_soc:.0f}%. Рекомендується зарядити акумулятор "
        "для підготовки до майбутнього споживання."
    ),
    (
        "Низький резерв енергії",
        "Акумулятор заряджений лише на {battery_soc:.0f}%, "
        "при цьому поточне споживання відсутнє. Доцільно "
        "відновити заряд акумулятора, щоб забезпечити резерв."
    ),
]


HIGH_LOAD_MESSAGES = [
    (
        "Високе споживання",
        "Поточне навантаження становить {load_power:.0f} Вт. "
        "Рекомендується вимкнути або відкласти роботу "
        "другорядних потужних приладів."
    ),
    (
        "Зменште навантаження",
        "Система зафіксувала високе споживання "
        "({load_power:.0f} Вт). Рекомендується тимчасово "
        "обмежити використання бойлера, електроплити "
        "або інших потужних приладів."
    ),
    (
        "Оптимізація споживання",
        "Поточне навантаження вище рекомендованого рівня. "
        "Перенесення частини енергоємних завдань на період "
        "активнішої сонячної генерації допоможе зменшити "
        "навантаження на акумулятор і мережу."
    )
]


# =========================================================
# НОВІ ПРОГНОЗНІ ПОВІДОМЛЕННЯ
# =========================================================

CURRENT_SURPLUS_FUTURE_DEFICIT_MESSAGES = [
    (
        "Підготуйтеся до майбутнього дефіциту",
        "Зараз доступний надлишок {balance:.0f} Вт, але о "
        "{time} прогнозується дефіцит близько {deficit:.0f} Вт. "
        "Рекомендується максимально використати поточний "
        "надлишок для заряджання акумулятора."
    ),
    (
        "Накопичте енергію зараз",
        "Поточна сонячна генерація перевищує споживання на "
        "{balance:.0f} Вт. За прогнозом, о {time} очікується "
        "дефіцит {deficit:.0f} Вт. Доцільно накопичити "
        "доступну енергію в акумуляторі."
    ),
    (
        "Збережіть енергію на майбутнє",
        "Поки сонячна генерація покриває навантаження, "
        "рекомендується використати надлишок для накопичення. "
        "О {time} прогнозується зниження доступної енергії "
        "приблизно на {deficit:.0f} Вт."
    )
]


CURRENT_SURPLUS_FULL_BATTERY_FUTURE_DEFICIT_MESSAGES = [
    (
        "Збережіть заряд акумулятора",
        "Акумулятор заряджений на {battery_soc:.0f}%, а зараз "
        "доступний надлишок {balance:.0f} Вт. О {time} прогнозується "
        "дефіцит близько {deficit:.0f} Вт. Не рекомендується "
        "відключати сонячні панелі — використайте надлишок "
        "для поточного енергоємного споживання."
    ),
    (
        "Використайте надлишок до погіршення генерації",
        "Зараз доступно {balance:.0f} Вт надлишкової сонячної "
        "енергії, але о {time} прогнозується дефіцит {deficit:.0f} Вт. "
        "Доцільно виконати енергоємні завдання зараз та залишити "
        "акумулятор як резерв."
    )
]


CURRENT_DEFICIT_FUTURE_SURPLUS_MESSAGES = [
    (
        "Перенесіть споживання на сонячний період",
        "Зараз спостерігається дефіцит {deficit:.0f} Вт, але о "
        "{time} прогнозується надлишок близько {surplus:.0f} Вт. "
        "Рекомендується перенести необов'язкові енергоємні "
        "завдання на цей період."
    ),
    (
        "Очікується кращий час для споживання",
        "Поточна сонячна генерація не покриває навантаження. "
        "За прогнозом, о {time} буде доступно приблизно "
        "{surplus:.0f} Вт надлишкової енергії. "
        "Доцільно відкласти заряджання електромобіля, "
        "роботу бойлера та інших потужних приладів."
    ),
    (
        "Відкладіть енергоємні завдання",
        "Зараз система має дефіцит {deficit:.0f} Вт. "
        "Підвищення сонячної генерації очікується о {time}. "
        "Рекомендується виконати потужні завдання пізніше, "
        "коли власної генерації буде більше."
    )
]


STABLE_SURPLUS_MESSAGES = [
    (
        "Тривалий сонячний надлишок",
        "За прогнозом, сонячна генерація залишатиметься вищою "
        "за споживання. Рекомендується запланувати заряджання "
        "електромобіля, нагрівання води або інші енергоємні завдання."
    ),
    (
        "Вдалий період для енергоємних завдань",
        "Найближчим часом очікується стабільний надлишок "
        "сонячної енергії. Це сприятливий період для "
        "використання потужних електроприладів."
    ),
    (
        "Використовуйте власну генерацію",
        "Прогноз показує стабільне перевищення сонячної "
        "генерації над споживанням. Доцільно збільшити "
        "корисне споживання власної сонячної енергії."
    )
]


STABLE_DEFICIT_MESSAGES = [
    (
        "Очікується тривалий дефіцит",
        "Прогноз показує, що найближчим часом споживання "
        "може перевищувати сонячну генерацію. "
        "Рекомендується обмежити необов'язкові навантаження."
    ),
    (
        "Плануйте споживання",
        "Найближчим часом прогнозується недостатня сонячна "
        "генерація. Доцільно перенести енергоємні завдання "
        "на період вищої генерації."
    )
]


FUTURE_DEFICIT_MESSAGES = [
    (
        "Підготуватися до дефіциту",
        "О {time} прогнозується дефіцит близько "
        "{deficit:.0f} Вт. Рекомендується заздалегідь "
        "зарядити акумулятор та перенести необов'язкові "
        "енергоємні завдання."
    ),
    (
        "Очікується зниження доступної енергії",
        "За прогнозом, о {time} генерація буде нижчою "
        "за споживання приблизно на {deficit:.0f} Вт. "
        "Доцільно використати поточний надлишок "
        "для накопичення енергії."
    ),
    (
        "Підготуйте акумулятор",
        "Прогноз показує дефіцит о {time}. "
        "Рекомендується максимально використати "
        "доступну сонячну енергію зараз та зменшити "
        "заплановані енергоємні навантаження."
    )
]


FUTURE_SURPLUS_MESSAGES = [
    (
        "Заплануйте енергоємні завдання",
        "О {time} прогнозується високий рівень сонячної "
        "генерації. Рекомендується запланувати на цей "
        "період заряджання електромобіля або роботу "
        "інших потужних приладів."
    ),
    (
        "Очікується сонячний надлишок",
        "Прогноз показує надлишок сонячної енергії "
        "о {time}. Доцільно перенести на цей період "
        "прання, нагрівання води або заряджання "
        "електромобіля."
    ),
    (
        "Оптимальний час для споживання",
        "О {time} очікується підвищена сонячна генерація. "
        "Використання енергоємних приладів у цей період "
        "дозволить краще використати власну генерацію."
    )
]


# =========================================================
# NOTIFICATION
# =========================================================

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


# =========================================================
# TARIFF
# =========================================================

def get_tariff_period(hour: int):
    if hour >= 23 or hour < 7:
        return "night"

    if 18 <= hour <= 22:
        return "peak"

    return "day"


# =========================================================
# CURRENT DATA
# =========================================================

def get_current_values(realtime_data):
    solar = realtime_data.get("solar", {})
    battery = realtime_data.get("battery", {})
    load = realtime_data.get("load", {})
    meter = realtime_data.get("meter", {})

    solar_power = float(solar.get("power", 0) or 0)
    battery_soc = float(battery.get("soc", 0) or 0)
    battery_power = float(battery.get("power", 0) or 0)
    load_power = float(load.get("load_power", 0) or 0)
    grid_power = float(meter.get("grid_power", 0) or 0)

    balance = solar_power - load_power

    return {
        "solar_power": solar_power,
        "battery_soc": battery_soc,
        "battery_power": battery_power,
        "load_power": load_power,
        "grid_power": grid_power,
        "balance": balance
    }


# =========================================================
# КРИТИЧНІ REALTIME-СПОВІЩЕННЯ
# =========================================================

def get_critical_recommendation(realtime_data):
    """
    Перевіряє тільки критичні поточні стани.
    Нічого не записує в БД.
    """

    current = get_current_values(realtime_data)

    solar_power = current["solar_power"]
    battery_soc = current["battery_soc"]
    load_power = current["load_power"]
    balance = current["balance"]

    # =====================================================
    # КРИТИЧНО НИЗЬКИЙ ЗАРЯД
    # =====================================================

    if (
        balance < DEFICIT_THRESHOLD
        and battery_soc <= CRITICAL_BATTERY
    ):
        selected = choose_message(
            CRITICAL_BATTERY_MESSAGES,
            battery_soc=battery_soc
        )

        return {
            "critical_key": "critical_battery",
            "priority": 100,
            "level": "danger",
            "source": "current",
            **selected,
            "solar_power": solar_power,
            "load_power": load_power,
            "battery_soc": battery_soc,
            "balance": balance
        }

    # =====================================================
    # КРИТИЧНИЙ НАДЛИШОК
    # =====================================================

    if (
        balance >= HIGH_SURPLUS_THRESHOLD
        and battery_soc >= FULL_BATTERY
    ):
        selected = choose_message(
            CRITICAL_SURPLUS_MESSAGES,
            balance=balance,
            battery_soc=battery_soc
        )

        return {
            "critical_key": "critical_surplus",
            "priority": 93,
            "level": "warning",
            "source": "current",
            **selected,
            "solar_power": solar_power,
            "load_power": load_power,
            "battery_soc": battery_soc,
            "balance": balance
        }

    return None


# =========================================================
# MESSAGE HELPER
# =========================================================

def choose_message(messages, **values):
    title, message = random.choice(messages)

    return {
        "title": title,
        "message": message.format(**values)
    }


# =========================================================
# FORECAST HELPERS
# =========================================================

def get_forecast_balance(item):
    if item.get("energy_balance") is not None:
        return float(item["energy_balance"])

    return float(
        item.get("solar_generation", 0)
        - item.get("total_consumption", 0)
    )


def get_future_deficit(forecast):
    periods = [
        item
        for item in forecast
        if get_forecast_balance(item) < DEFICIT_THRESHOLD
    ]

    if not periods:
        return None

    return min(
        periods,
        key=get_forecast_balance
    )

def get_future_surplus(forecast):
    periods = [
        item
        for item in forecast
        if get_forecast_balance(item) > SURPLUS_THRESHOLD
    ]

    if not periods:
        return None

    return max(
        periods,
        key=get_forecast_balance
    )


def get_future_energy_trend(forecast):
    """
    Визначає загальну тенденцію найближчого прогнозу.

    Можливі значення:
    - surplus_to_deficit
    - deficit_to_surplus
    - stable_surplus
    - stable_deficit
    - None
    """

    if not forecast or len(forecast) < 2:
        return None

    balances = [
        get_forecast_balance(item)
        for item in forecast
    ]

    current_balance = balances[0]
    future_balances = balances[1:]

    if (
        current_balance > SURPLUS_THRESHOLD
        and any(
            balance < DEFICIT_THRESHOLD
            for balance in future_balances
        )
    ):
        return "surplus_to_deficit"

    if (
        current_balance < DEFICIT_THRESHOLD
        and any(
            balance > SURPLUS_THRESHOLD
            for balance in future_balances
        )
    ):
        return "deficit_to_surplus"

    if (
        current_balance > SURPLUS_THRESHOLD
        and all(
            balance > SURPLUS_THRESHOLD
            for balance in future_balances
        )
    ):
        return "stable_surplus"

    if (
        current_balance < DEFICIT_THRESHOLD
        and all(
            balance < DEFICIT_THRESHOLD
            for balance in future_balances
        )
    ):
        return "stable_deficit"

    return None


# =========================================================
# PRIORITY ENGINE
# =========================================================

def generate_priority_recommendation(
    db: Session,
    user_id: int,
    realtime_data,
    forecast_data=None
):
    current = get_current_values(realtime_data)

    # Якщо прогноз переданий вручну — використовуємо його.
    # Якщо ні — отримуємо автоматичний прогноз.
    forecast = (
        forecast_data
        if forecast_data is not None
        else forecast_24h()
    )

    analytics = get_energy_analytics(db)

    candidates = []

    solar_power = current["solar_power"]
    battery_soc = current["battery_soc"]
    load_power = current["load_power"]
    grid_power = current["grid_power"]
    balance = current["balance"]

    # =====================================================
    # ПРОГНОЗ
    # =====================================================

    worst_deficit = get_future_deficit(forecast)
    best_surplus = get_future_surplus(forecast)
    forecast_trend = get_future_energy_trend(forecast)

    # =====================================================
    # 1. КРИТИЧНИЙ ДЕФІЦИТ + НИЗЬКИЙ SOC
    # =====================================================

    if (
        balance < DEFICIT_THRESHOLD
        and battery_soc <= CRITICAL_BATTERY
    ):
        selected = choose_message(
            CRITICAL_BATTERY_MESSAGES,
            battery_soc=battery_soc
        )

        candidates.append({
            "priority": 100,
            "level": "danger",
            "source": "current",
            **selected
        })

    # =====================================================
    # 2. НИЗЬКИЙ SOC + ДЕФІЦИТ
    # =====================================================

    elif (
        balance < DEFICIT_THRESHOLD
        and battery_soc < LOW_BATTERY
    ):
        selected = choose_message(
            LOW_BATTERY_MESSAGES,
            deficit=abs(balance),
            battery_soc=battery_soc
        )

        candidates.append({
            "priority": 95,
            "level": "warning",
            "source": "current",
            **selected
        })

    # =====================================================
    # 3. ПОТОЧНИЙ НАДЛИШОК + МАЙБУТНІЙ ДЕФІЦИТ
    # =====================================================

    if (
        forecast_trend == "surplus_to_deficit"
        and balance > SURPLUS_THRESHOLD
        and worst_deficit is not None
    ):
        deficit = abs(
            get_forecast_balance(worst_deficit)
        )

        # Якщо акумулятор ще не повний —
        # накопичуємо енергію.
        if battery_soc < FULL_BATTERY:
            selected = choose_message(
                CURRENT_SURPLUS_FUTURE_DEFICIT_MESSAGES,
                balance=balance,
                time=worst_deficit["time"],
                deficit=deficit
            )

            candidates.append({
                "priority": 98,
                "level": "warning",
                "source": "forecast",
                **selected
            })

        # Якщо акумулятор уже повний —
        # не радимо відключати панелі, бо попереду дефіцит.
        else:
            selected = choose_message(
                CURRENT_SURPLUS_FULL_BATTERY_FUTURE_DEFICIT_MESSAGES,
                balance=balance,
                battery_soc=battery_soc,
                time=worst_deficit["time"],
                deficit=deficit
            )

            candidates.append({
                "priority": 97,
                "level": "warning",
                "source": "forecast",
                **selected
            })

    # =====================================================
    # 4. ПОТОЧНИЙ ДЕФІЦИТ + МАЙБУТНІЙ НАДЛИШОК
    # =====================================================

    if (
        forecast_trend == "deficit_to_surplus"
        and balance < DEFICIT_THRESHOLD
        and best_surplus is not None
    ):
        surplus = get_forecast_balance(best_surplus)

        selected = choose_message(
            CURRENT_DEFICIT_FUTURE_SURPLUS_MESSAGES,
            deficit=abs(balance),
            time=best_surplus["time"],
            surplus=surplus
        )

        candidates.append({
            "priority": 94,
            "level": "info",
            "source": "forecast",
            **selected
        })

    # =====================================================
    # 5. СТАБІЛЬНИЙ НАДЛИШОК
    # =====================================================

    if (
        forecast_trend == "stable_surplus"
        and balance > SURPLUS_THRESHOLD
        and battery_soc >= FULL_BATTERY
    ):
        selected = choose_message(
            STABLE_SURPLUS_MESSAGES
        )

        candidates.append({
            "priority": 91,
            "level": "info",
            "source": "forecast",
            **selected
        })

    # =====================================================
    # 6. СТАБІЛЬНИЙ ДЕФІЦИТ
    # =====================================================

    if forecast_trend == "stable_deficit":
        selected = choose_message(
            STABLE_DEFICIT_MESSAGES
        )

        candidates.append({
            "priority": 86,
            "level": "warning",
            "source": "forecast",
            **selected
        })

    # =====================================================
    # 7. ВЕЛИКИЙ ПОТОЧНИЙ ДЕФІЦИТ
    # =====================================================

    if balance < HIGH_DEFICIT_THRESHOLD:
        selected = choose_message(
            CURRENT_DEFICIT_MESSAGES,
            solar_power=solar_power,
            load_power=load_power,
            battery_soc=battery_soc,
            deficit=abs(balance)
        )

        candidates.append({
            "priority": 88,
            "level": "warning",
            "source": "current",
            **selected
        })

    # =====================================================
    # 8. ПОТОЧНИЙ ДЕФІЦИТ
    # =====================================================

    elif balance < DEFICIT_THRESHOLD:
        selected = choose_message(
            CURRENT_DEFICIT_MESSAGES,
            solar_power=solar_power,
            load_power=load_power,
            battery_soc=battery_soc,
            deficit=abs(balance)
        )

        candidates.append({
            "priority": 82,
            "level": "info",
            "source": "current",
            **selected
        })

    # =====================================================
    # 9. ПОТОЧНИЙ НАДЛИШОК + БАТАРЕЯ НЕ ПОВНА
    # =====================================================

    if (
        balance > SURPLUS_THRESHOLD
        and battery_soc < FULL_BATTERY
        and forecast_trend != "surplus_to_deficit"
    ):
        selected = choose_message(
            SURPLUS_BATTERY_MESSAGES,
            balance=balance,
            battery_soc=battery_soc
        )

        candidates.append({
            "priority": 75,
            "level": "info",
            "source": "current",
            **selected
        })

    # =====================================================
    # 10. НАДЛИШОК + ПОВНА БАТАРЕЯ
    # =====================================================

    if (
        balance > SURPLUS_THRESHOLD
        and battery_soc >= FULL_BATTERY
        and forecast_trend != "surplus_to_deficit"
    ):
        selected = choose_message(
            FULL_BATTERY_SURPLUS_MESSAGES,
            balance=balance,
            battery_soc=battery_soc,
            solar_power=solar_power,
            load_power=load_power
        )

        candidates.append({
            "priority": 78,
            "level": "info",
            "source": "current",
            **selected
        })

    # =====================================================
    # 11. ДУЖЕ ВЕЛИКИЙ НАДЛИШОК
    # =====================================================

    if (
        balance >= HIGH_SURPLUS_THRESHOLD
        and battery_soc >= FULL_BATTERY
        and forecast_trend != "surplus_to_deficit"
    ):
        selected = choose_message(
            CRITICAL_SURPLUS_MESSAGES,
            balance=balance,
            battery_soc=battery_soc
        )

        candidates.append({
            "priority": 93,
            "level": "warning",
            "source": "current",
            **selected
        })

    # =====================================================
    # 12. ВИСОКЕ ПОТОЧНЕ НАВАНТАЖЕННЯ
    # =====================================================

    if load_power >= HIGH_LOAD:
        selected = choose_message(
            HIGH_LOAD_MESSAGES,
            load_power=load_power
        )

        candidates.append({
            "priority": 72,
            "level": "warning",
            "source": "analytics",
            **selected
        })

    # =====================================================
    # 13. МАЙБУТНІЙ ДЕФІЦИТ
    # =====================================================

    if (
        worst_deficit is not None
        and forecast_trend != "surplus_to_deficit"
    ):
        deficit = abs(
            get_forecast_balance(worst_deficit)
        )

        priority = 80

        peak_hour = analytics.get(
            "peak_consumption_hour"
        )

        try:
            forecast_hour = int(
                worst_deficit["time"].split(":")[0]
            )
        except (KeyError, ValueError, AttributeError):
            forecast_hour = None

        if (
            peak_hour is not None
            and peak_hour == forecast_hour
        ):
            priority += 10

        selected = choose_message(
            FUTURE_DEFICIT_MESSAGES,
            time=worst_deficit["time"],
            deficit=deficit
        )

        candidates.append({
            "priority": priority,
            "level": "warning",
            "source": "forecast",
            **selected
        })

    # =====================================================
    # 14. МАЙБУТНІЙ НАДЛИШОК
    # =====================================================

    if (
        best_surplus is not None
        and forecast_trend != "deficit_to_surplus"
    ):
        surplus = get_forecast_balance(
            best_surplus
        )

        selected = choose_message(
            FUTURE_SURPLUS_MESSAGES,
            time=best_surplus["time"]
        )

        candidates.append({
            "priority": 65,
            "level": "info",
            "source": "forecast",
            **selected,
            "forecast_surplus": round(
                surplus,
                2
            )
        })

    # =====================================================
    # 15. НЕМАЄ СОНЦЯ + НЕМАЄ НАВАНТАЖЕННЯ + НИЗЬКИЙ SOC
    # =====================================================

    if (
        solar_power <= 0
        and load_power <= 0
        and battery_soc <= LOW_BATTERY
    ):
        selected = choose_message(
            IDLE_EMPTY_BATTERY_MESSAGES,
            battery_soc=battery_soc
        )

        candidates.append({
            "priority": 90,
            "level": "warning",
            "source": "current",
            **selected
        })

    # =====================================================
    # 16. АНАЛІТИКА ПІКОВОГО СПОЖИВАННЯ
    # =====================================================

    peak_hour = analytics.get(
        "peak_consumption_hour"
    )

    if peak_hour is not None:
        candidates.append({
            "priority": 45,
            "level": "info",
            "source": "analytics",
            "title": "Контролювати навантаження у піковий період",
            "message": (
                f"За історичними даними найвище "
                f"середнє споживання спостерігається "
                f"близько {peak_hour:02d}:00. "
                f"Рекомендується виконувати частину "
                f"енергоємних завдань у періоди "
                f"вищої сонячної генерації."
            )
        })

    # =====================================================
    # 17. АНАЛІТИКА СОНЯЧНОЇ ГЕНЕРАЦІЇ
    # =====================================================

    peak_solar_hour = analytics.get(
        "peak_solar_hour"
    )

    if peak_solar_hour is not None:
        candidates.append({
            "priority": 40,
            "level": "info",
            "source": "analytics",
            "title": "Оптимальний період сонячної генерації",
            "message": (
                f"За історичними даними найвища "
                f"сонячна генерація спостерігається "
                f"близько {peak_solar_hour:02d}:00. "
                f"Рекомендується планувати енергоємні "
                f"завдання ближче до цього періоду."
            )
        })

    # =====================================================
    # 18. НЕМАЄ ОСОБЛИВИХ СИТУАЦІЙ
    # =====================================================

    if not candidates:
        candidates.append({
            "priority": 10,
            "level": "info",
            "source": "current",
            "title": "Система працює оптимально",
            "message": (
                f"Поточний енергетичний баланс стабільний. "
                f"Сонячна генерація: "
                f"{solar_power:.0f} Вт, "
                f"споживання: "
                f"{load_power:.0f} Вт, "
                f"заряд акумулятора: "
                f"{battery_soc:.0f}%."
            )
        })

    # =====================================================
    # ВИБІР НАЙВАЖЛИВІШОЇ РЕКОМЕНДАЦІЇ
    # =====================================================

    recommendation = max(
        candidates,
        key=lambda x: x["priority"]
    )

    # =====================================================
    # ДОДАТКОВІ ДАНІ
    # =====================================================

    recommendation["solar_power"] = solar_power
    recommendation["load_power"] = load_power
    recommendation["battery_soc"] = battery_soc
    recommendation["grid_power"] = grid_power
    recommendation["battery_power"] = current["battery_power"]
    recommendation["balance"] = balance
    recommendation["tariff"] = get_tariff_period(
        datetime.now().hour
    )

    if forecast_trend is not None:
        recommendation["forecast_trend"] = forecast_trend

    if worst_deficit is not None:
        recommendation["forecast_deficit_time"] = (
            worst_deficit["time"]
        )

        recommendation["forecast_deficit"] = round(
            abs(
                get_forecast_balance(
                    worst_deficit
                )
            ),
            2
        )

    if best_surplus is not None:
        recommendation["forecast_surplus_time"] = (
            best_surplus["time"]
        )

        recommendation["forecast_surplus"] = round(
            get_forecast_balance(
                best_surplus
            ),
            2
        )

    return recommendation


# =========================================================
# ГОЛОВНА ФУНКЦІЯ
# =========================================================

def generate_energy_recommendations(
    db: Session,
    user_id: int,
    realtime_data,
    forecast_data=None
):
    recommendation = generate_priority_recommendation(
        db=db,
        user_id=user_id,
        realtime_data=realtime_data,
        forecast_data=forecast_data
    )

    create_notification(
        db=db,
        user_id=user_id,
        title=recommendation["title"],
        message=recommendation["message"],
        level=recommendation["level"]
    )

    return recommendation


# =========================================================
# ПРОГНОЗНІ РЕКОМЕНДАЦІЇ
# =========================================================

def get_forecast_recommendations():
    forecast = forecast_24h()

    recommendations = []

    if not forecast:
        return recommendations

    peak_load = max(
        forecast,
        key=lambda x: x["total_consumption"]
    )

    recommendations.append({
        "type": "forecast_peak_load",
        "title": "Очікується підвищене споживання",
        "message": (
            f"Найвище прогнозоване споживання "
            f"очікується о {peak_load['time']}. "
            f"Рекомендується заздалегідь перенести "
            f"частину енергоємних завдань."
        ),
        "level": "warning"
    })

    peak_solar = max(
        forecast,
        key=lambda x: x["solar_generation"]
    )

    recommendations.append({
        "type": "forecast_solar",
        "title": "Очікується висока сонячна генерація",
        "message": (
            f"Найвища сонячна генерація "
            f"очікується о {peak_solar['time']}. "
            f"Цей період доцільно використати "
            f"для заряджання електромобіля, "
            f"акумулятора або роботи потужних приладів."
        ),
        "level": "info"
    })

    worst_deficit = get_future_deficit(
        forecast
    )

    if worst_deficit is not None:
        deficit = abs(
            get_forecast_balance(
                worst_deficit
            )
        )

        recommendations.append({
            "type": "forecast_deficit",
            "title": "Очікується дефіцит енергії",
            "message": (
                f"О {worst_deficit['time']} "
                f"прогнозується дефіцит близько "
                f"{deficit:.0f} Вт. "
                f"Рекомендується заздалегідь "
                f"зарядити акумулятор та перенести "
                f"необов'язкові енергоємні завдання."
            ),
            "level": "warning"
        })

    best_surplus = get_future_surplus(
        forecast
    )

    if best_surplus is not None:
        surplus = get_forecast_balance(
            best_surplus
        )

        recommendations.append({
            "type": "forecast_surplus",
            "title": "Очікується надлишок сонячної енергії",
            "message": (
                f"О {best_surplus['time']} "
                f"прогнозується надлишок близько "
                f"{surplus:.0f} Вт. "
                f"Рекомендується запланувати "
                f"енергоємні завдання на цей період."
            ),
            "level": "info"
        })

    return recommendations



# =========================================================
# РЕКОМЕНДАЦІЇ НА ДЕНЬ
# =========================================================

def get_day_recommendations():

    forecast = forecast_24h()

    if not forecast:
        return []

    recommendations = []

    # =====================================================
    # НАЙБІЛЬШЕ СПОЖИВАННЯ
    # =====================================================

    peak_load = max(
        forecast,
        key=lambda item: item.get(
            "total_consumption",
            0
        )
    )

    recommendations.append({
        "type": "forecast_peak_load",
        "time": peak_load["time"],
        "priority": 65,
        "level": "info",
        "title": "Очікується підвищене споживання",
        "message": (
            f"О {peak_load['time']} прогнозується "
            f"найвище споживання за період. "
            f"Рекомендується заздалегідь перенести "
            f"необов'язкові енергоємні завдання "
            f"на період вищої сонячної генерації."
        ),
        "total_consumption": round(
            peak_load["total_consumption"],
            2
        ),
        "energy_balance": round(
            get_forecast_balance(peak_load),
            2
        )
    })

    # =====================================================
    # НАЙВИЩА СОНЯЧНА ГЕНЕРАЦІЯ
    # =====================================================

    peak_solar = max(
        forecast,
        key=lambda item: item.get(
            "solar_generation",
            0
        )
    )

    recommendations.append({
        "type": "forecast_solar",
        "time": peak_solar["time"],
        "priority": 65,
        "level": "info",
        "title": "Оптимальний час для використання сонячної енергії",
        "message": (
            f"О {peak_solar['time']} прогнозується "
            f"найвища сонячна генерація — "
            f"{peak_solar['solar_generation']:.0f} Вт. "
            f"Доцільно запланувати на цей період "
            f"енергоємні завдання або заряджання."
        ),
        "solar_generation": round(
            peak_solar["solar_generation"],
            2
        ),
        "energy_balance": round(
            get_forecast_balance(peak_solar),
            2
        )
    })

    # =====================================================
    # НАЙБІЛЬШИЙ МАЙБУТНІЙ ДЕФІЦИТ
    # =====================================================

    worst_deficit = get_future_deficit(
        forecast
    )

    if worst_deficit is not None:

        deficit = abs(
            get_forecast_balance(
                worst_deficit
            )
        )

        recommendations.append({
            "type": "forecast_deficit",
            "time": worst_deficit["time"],
            "priority": 90,
            "level": "warning",
            "title": "Підготуйтеся до майбутнього дефіциту",
            "message": (
                f"О {worst_deficit['time']} "
                f"прогнозується дефіцит близько "
                f"{deficit:.0f} Вт. "
                f"Рекомендується заздалегідь "
                f"зарядити акумулятор та перенести "
                f"необов'язкові енергоємні завдання."
            ),
            "energy_balance": round(
                get_forecast_balance(
                    worst_deficit
                ),
                2
            )
        })

    # =====================================================
    # НАЙБІЛЬШИЙ МАЙБУТНІЙ НАДЛИШОК
    # =====================================================

    best_surplus = get_future_surplus(
        forecast
    )

    if best_surplus is not None:

        surplus = get_forecast_balance(
            best_surplus
        )

        recommendations.append({
            "type": "forecast_surplus",
            "time": best_surplus["time"],
            "priority": 75,
            "level": "info",
            "title": "Оптимальний час для споживання",
            "message": (
                f"О {best_surplus['time']} "
                f"прогнозується надлишок близько "
                f"{surplus:.0f} Вт. "
                f"Доцільно виконати в цей період "
                f"енергоємні завдання."
            ),
            "energy_balance": round(
                surplus,
                2
            )
        })

    # =====================================================
    # СОРТУВАННЯ ЗА ЧАСОМ
    # =====================================================

    recommendations.sort(
        key=lambda item: item["time"]
    )

    return recommendations

# =========================================================
# АНАЛІТИЧНІ РЕКОМЕНДАЦІЇ
# =========================================================

def get_analytics_recommendations(db: Session):
    analytics = get_energy_analytics(db)

    if not analytics.get("has_data"):
        return []

    recommendations = []

    if analytics.get("peak_consumption_hour") is not None:
        hour = analytics[
            "peak_consumption_hour"
        ]

        recommendations.append({
            "type": "historical_peak",
            "title": "Виявлено період високого споживання",
            "message": (
                f"За історичними даними найвище "
                f"середнє споживання спостерігається "
                f"близько {hour:02d}:00. "
                f"Рекомендується переносити частину "
                f"енергоємних завдань на період "
                f"вищої сонячної генерації."
            ),
            "level": "info"
        })

    if analytics.get("peak_solar_hour") is not None:
        hour = analytics[
            "peak_solar_hour"
        ]

        recommendations.append({
            "type": "historical_solar",
            "title": "Виявлено період максимальної генерації",
            "message": (
                f"За історичними даними найвища "
                f"сонячна генерація спостерігається "
                f"близько {hour:02d}:00. "
                f"Цей час доцільно використовувати "
                f"для енергоємних завдань."
            ),
            "level": "info"
        })

    return recommendations