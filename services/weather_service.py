import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)


CITY_TRANSLATIONS = {
    "киев": "Kyiv", "києв": "Kyiv", "киевe": "Kyiv", "kyiv": "Kyiv",
    "москва": "Moscow", "moscow": "Moscow",
    "харьков": "Kharkiv", "харків": "Kharkiv", "kharkiv": "Kharkiv",
    "одесса": "Odesa", "одеса": "Odesa", "odessa": "Odesa",
    "днепр": "Dnipro", "дніпро": "Dnipro", "dnipro": "Dnipro",
    "львов": "Lviv", "львів": "Lviv", "lviv": "Lviv",
    "лондон": "London", "london": "London",
    "париж": "Paris", "paris": "Paris",
    "берлин": "Berlin", "berlin": "Berlin",
    "варшава": "Warsaw", "warsaw": "Warsaw",
    "нью-йорк": "New York", "нью йорк": "New York", "new york": "New York",
    "прага": "Prague", "prague": "Prague",
    "рим": "Rome", "rome": "Rome",
    "мадрид": "Madrid", "madrid": "Madrid",
    "токио": "Tokyo", "tokyo": "Tokyo",
    "пекин": "Beijing", "beijing": "Beijing",
    "стамбул": "Istanbul", "istanbul": "Istanbul",
    "дубай": "Dubai", "dubai": "Dubai",
    "амстердам": "Amsterdam", "amsterdam": "Amsterdam",
    "вена": "Vienna", "vienna": "Vienna",
    "будапешт": "Budapest", "budapest": "Budapest",
    "софия": "Sofia", "sofia": "Sofia",
    "бухарест": "Bucharest", "bucharest": "Bucharest",
}


async def get_coordinates(city: str, country_hint: str = None) -> dict | None:
    """Получает координаты города через Open-Meteo Geocoding API."""
    city_lower = city.lower().strip()
    english_city = CITY_TRANSLATIONS.get(city_lower, city)

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": english_city, "count": 10, "language": "en", "format": "json"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        results = data.get("results", [])
        if not results:
            return None

        if city_lower in ["киев", "києв", "kyiv", "kiev"]:
            for res in results:
                if res.get("country_code") == "UA":
                    return {
                        "name": res.get("name"),
                        "country": res.get("country"),
                        "latitude": res.get("latitude"),
                        "longitude": res.get("longitude"),
                    }

        if country_hint:
            for res in results:
                if country_hint.lower() in (res.get("country", "") or "").lower():
                    return {
                        "name": res.get("name"),
                        "country": res.get("country"),
                        "latitude": res.get("latitude"),
                        "longitude": res.get("longitude"),
                    }

        result = results[0]
        return {
            "name": result.get("name"),
            "country": result.get("country"),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
        }
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None


async def _fetch_weather_open_meteo(lat: float, lon: float) -> dict | None:
    """Один запрос к Open-Meteo. Возвращает None если данных нет."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        current = data.get("current", {})
        temp = current.get("temperature_2m")

        # Ключевая проверка: если температуры нет — считаем запрос неудачным
        if temp is None:
            logger.warning(f"Open-Meteo returned no temperature for {lat},{lon}")
            return None

        return {
            "temperature": temp,
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind": current.get("wind_speed_10m"),
            "code": current.get("weather_code"),
            "description": _weather_code_to_text(current.get("weather_code")),
        }
    except Exception as e:
        logger.error(f"Open-Meteo error: {e}")
        return None


async def _fetch_weather_wttr(city: str) -> dict | None:
    """Fallback: wttr.in — другой бесплатный API."""
    url = f"https://wttr.in/{city}"
    params = {"format": "j1"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params, headers={"User-Agent": "curl/8.0"})
            r.raise_for_status()
            data = r.json()

        current = data.get("current_condition", [{}])[0]
        if not current:
            return None

        temp = current.get("temp_C")
        if temp is None:
            return None

        # wttr отдаёт строки, конвертим в числа
        def to_float(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        return {
            "temperature": to_float(temp),
            "feels_like": to_float(current.get("FeelsLikeC")),
            "humidity": to_float(current.get("humidity")),
            "wind": to_float(current.get("windspeedKmph")),
            "code": None,
            "description": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
        }
    except Exception as e:
        logger.error(f"wttr.in error: {e}")
        return None


async def get_weather(city: str) -> dict | None:
    """Получает погоду. Пробует Open-Meteo с retry, потом wttr.in."""
    coords = await get_coordinates(city)
    if not coords:
        return None

    # Пробуем Open-Meteo 2 раза с паузой
    for attempt in range(2):
        data = await _fetch_weather_open_meteo(coords["latitude"], coords["longitude"])
        if data:
            return {
                "city": coords["name"],
                "country": coords["country"],
                **data,
            }
        if attempt == 0:
            await asyncio.sleep(1)

    # Fallback на wttr.in
    logger.info(f"Open-Meteo failed for {city}, trying wttr.in...")
    data = await _fetch_weather_wttr(coords["name"])
    if data:
        return {
            "city": coords["name"],
            "country": coords["country"],
            **data,
        }

    return None


def _weather_code_to_text(code: int) -> str:
    """Переводит WMO код в текст."""
    if code is None:
        return "Unknown"

    codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown")


def format_weather(w: dict, lang: str = "en") -> str:
    """Форматирует погоду для отправки в чат."""
    titles = {
        "en": f"🌤 Weather in {w['city']}, {w['country']}",
        "ru": f"🌤 Погода в {w['city']}, {w['country']}",
        "uk": f"🌤 Погода у {w['city']}, {w['country']}",
    }
    labels = {
        "en": {"temp": "Temperature", "feels": "Feels like", "humidity": "Humidity", "wind": "Wind", "cond": "Condition"},
        "ru": {"temp": "Температура", "feels": "Ощущается как", "humidity": "Влажность", "wind": "Ветер", "cond": "Состояние"},
        "uk": {"temp": "Температура", "feels": "Відчувається як", "humidity": "Вологість", "wind": "Вітер", "cond": "Стан"},
    }
    L = labels.get(lang, labels["en"])

    def fmt(v, suffix=""):
        return f"{v}{suffix}" if v is not None else "—"

    return (
        f"{titles.get(lang, titles['en'])}\n\n"
        f"🌡 {L['temp']}: {fmt(w['temperature'], '°C')}\n"
        f"🤔 {L['feels']}: {fmt(w['feels_like'], '°C')}\n"
        f"💧 {L['humidity']}: {fmt(w['humidity'], '%')}\n"
        f"💨 {L['wind']}: {fmt(w['wind'], ' km/h')}\n"
        f"☁️ {L['cond']}: {w.get('description') or '—'}"
    )