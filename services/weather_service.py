import httpx
import logging

logger = logging.getLogger(__name__)


# Словарь популярных городов (русское/украинское → английское)
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
            data = r.json()

        results = data.get("results", [])
        if not results:
            return None

        # Для Киева — приоритет Украины
        if city_lower in ["киев", "києв", "kyiv", "kiev"]:
            for res in results:
                if res.get("country_code") == "UA":
                    return {
                        "name": res.get("name"),
                        "country": res.get("country"),
                        "latitude": res.get("latitude"),
                        "longitude": res.get("longitude"),
                    }

        # Если есть подсказка по стране — фильтруем
        if country_hint:
            for res in results:
                if country_hint.lower() in (res.get("country", "") or "").lower():
                    return {
                        "name": res.get("name"),
                        "country": res.get("country"),
                        "latitude": res.get("latitude"),
                        "longitude": res.get("longitude"),
                    }

        # Иначе — первый результат
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


async def get_weather(city: str) -> dict | None:
    """Получает текущую погоду для города."""
    coords = await get_coordinates(city)
    if not coords:
        return None

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            data = r.json()

        current = data.get("current", {})
        return {
            "city": coords["name"],
            "country": coords["country"],
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind": current.get("wind_speed_10m"),
            "code": current.get("weather_code"),
            "description": _weather_code_to_text(current.get("weather_code")),
        }
    except Exception as e:
        logger.error(f"Weather error: {e}")
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

    return (
        f"{titles.get(lang, titles['en'])}\n\n"
        f"🌡 {L['temp']}: {w['temperature']}°C\n"
        f"🤔 {L['feels']}: {w['feels_like']}°C\n"
        f"💧 {L['humidity']}: {w['humidity']}%\n"
        f"💨 {L['wind']}: {w['wind']} km/h\n"
        f"☁️ {L['cond']}: {w['description']}"
    )