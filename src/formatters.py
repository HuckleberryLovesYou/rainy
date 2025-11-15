import datetime
from exceptions import FormatError
from models import LocalDateTime

_EMOJI_MAP: dict[str, str] = {
    "city": "\U0001F3E0",
    "weather": "\U000026C5",
    "temperature": "\U0001F321",
    "wind speed": "\U0001F4A8",
    "wind direction": "\U0001F9ED",
    "sunrise": "\U0001F305",
    "sunset": "\U0001F307",
    "date": "\U0001F4C5",
    "time": "\U000023F0",
    "precipitation": "\U0001F327",
    "surface pressure": "\U0001F39A",
    "humidity": "\U0001F4A7",
    "uv index": "\U00002600"
}

_DATE_FORMAT_MAP: dict[str, str] = {
    "MM/DD/YYYY": "%m/%d/%Y",
    "DD/MM/YYYY": "%d/%m/%Y",
    "YYYY/MM/DD": "%Y/%m/%d",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD.MM.YYYY": "%d.%m.%Y"
}

def get_local_date_time(utc_time_offset_seconds, sunrise, sunset, date_format, time_format) -> LocalDateTime:
    time_at_location = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=utc_time_offset_seconds)
    date_format_str = _DATE_FORMAT_MAP.get(date_format)
    if date_format_str is None:
        raise FormatError(f"The date format configured {date_format!r} wasn't matched with any supported format.")
    local_date = time_at_location.strftime(date_format_str)

    if time_format == 12:
        local_time = time_at_location.strftime("%I:%M:%S %p")
        sunrise_time_obj = datetime.datetime.strptime(sunrise, "%H:%M")
        local_sunrise = sunrise_time_obj.strftime("%I:%M %p")
        sunset_time_obj = datetime.datetime.strptime(sunset, "%H:%M")
        local_sunset = sunset_time_obj.strftime("%I:%M %p")
    elif time_format == 24:
        local_time = time_at_location.strftime("%H:%M:%S")
        local_sunrise = sunrise
        local_sunset = sunset
    else:
        raise FormatError(f"The time format configured {time_format!r} wasn't matched with any supported format.")

    local_date_time = LocalDateTime(
        local_date=local_date,
        local_time=local_time,
        local_sunrise=local_sunrise,
        local_sunset=local_sunset,
    )

    return local_date_time


def get_emoji(key: str) -> str:
    """
    Returns a Unicode emoji corresponding to the provided weather-related key.

    This function maps specific string keys (such as "city", "weather", "temperature", etc.)
    to their representative emoji for use in the Rainy CLI output. If the key is not recognized
    or is unset, a FormatError exception is raised.

    Supported keys include:
        - "city": 🏠
        - "weather": ⛅
        - "temperature": 🌡️
        - "wind speed": 💨
        - "wind direction": 🧭
        - "sunrise": 🌅
        - "sunset": 🌇
        - "date": 📅
        - "time": ⏰
        - "precipitation": 🌧️
        - "surface pressure": 🎚️
        - "humidity": 💧
        - "uv index": ☀️

    :param key: The string key representing a weather attribute for which to get an emoji.
    :type key: str
    :return: The emoji string representing the key, or an empty string if the key is invalid or unset.
    :rtype: str
    """
    emoji = _EMOJI_MAP.get(key.lower(), "")
    return emoji


def get_wind_direction(wind_direction: int) -> str:
    if wind_direction >= 315 or wind_direction < 45:
        direction = "North"
    elif wind_direction < 135:
        direction = "East"
    elif wind_direction < 225:
        direction = "South"
    else:  # 225 <= wind_direction < 315
        direction = "West"

    return f"{wind_direction} ({direction})"


def get_air_quality_index_concern(air_quality_index: int) -> str:
    if air_quality_index <= 50:
        return "Good"
    elif air_quality_index <= 100:
        return "Moderate"
    elif air_quality_index <= 150:
        return "Unhealthy for Sensitive Groups"
    elif air_quality_index <= 200:
        return "Unhealthy"
    elif air_quality_index <= 300:
        return "Very Unhealthy"
    elif air_quality_index > 300:
        return "Hazardous"
    else:
        return "Could not be determined"


def get_ascii_art(weather_code: int, is_day: bool) -> list[str]:
    """Gets the ascii art for the passed weather_code and returns it in a list as well as the friendly name of the current weather.

    :param weather_code: The code of the current weather returned by the API (a WMO Weather interpretation code (WW) 1-99. Further Information here: https://open-meteo.com/en/docs).
    :type weather_code: int
    :param is_day: Changes the output to sun or moon if the weather_code stands for 'clear' (Weather code = 0) [Default=True]
    :type weather_code: boolean

    :returns: tuple: It contains a list of the ascii art, where on each index there's a single line of the ascii art.
    """
    if weather_code == 0:
        if is_day:
            return [
                r"                 ",
                r"      \   /      ",
                r"       .-.       ",
                r"    ‒ (   ) ‒    ",
                r"       `-᾿       ",
                r"      /   \      ",
                r"                 "
            ]
        else:
            return [
                r"                 ",
                r"        _.._     ",
                r"      .' .-'`    ",
                r"     /  /        ",
                r"     |  |        ",
                r"     \  \        ",
                r"      '._'-._    ",
                r"         ```     "
            ]

    elif weather_code in [1, 2, 3]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"                 ",
            r"                 ",
            r"                 ",
        ]
    elif weather_code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"    ʻ‚ʻ‚ʻ‚ʻ‚ʻ    ",
            r"                 ",
            r"                 ",
        ]
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"    * * * * *    ",
            r"                 ",
            r"                 ",
        ]
    elif weather_code in [95, 96, 99]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"        /_       ",
            r"         /       ",
            r"                 ",
        ]
    else:
        return [
            r"                 ",
            r"~~~~   ~~~~ ~~~  ",
            r"~~~   *  ~~~~~  *",
            r"  ~~~~  ~~~ * ~~~",
            r"~~~~*   ~~~~   * ",
            r"  * ~~~ ~~~~  ~~~",
            r"                 "
        ]


def get_weather_name(weather_code: int) -> str:
    if weather_code == 0:
        return "clear"
    elif weather_code in [1, 2, 3]:
        return "cloudy"
    elif weather_code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return "rainy"
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return "snowy"
    elif weather_code in [95, 96, 99]:
        return "thundery"
    else:
        return "foggy"

def get_wind_speed(wind_speed, unit: str) -> str:
    return f"{wind_speed} {unit}"

def get_temperature(temperature: float, apparent_temperature: float, temperature_min: float, temperature_max: float, unit: str, show_apparent_temperature: bool, show_max_and_min_temperature: bool) -> str:
    temperature_str: str = f"{temperature}{unit}"

    if show_apparent_temperature:
        temperature_str += f" feels like {apparent_temperature}{unit}"
    if show_max_and_min_temperature:
        temperature_str += f" ({temperature_max}{unit} ↑ | {temperature_min}{unit} ↓)"

    return temperature_str

def get_humidity(humidity: int) -> str:
    return str(humidity) + " %"

def get_precipitation(precipitation: float, unit) -> str:
    return str(precipitation) + f" {unit} →1h"

def get_surface_pressure(surface_pressure: float) -> str:
    return str(surface_pressure) + " hPa"