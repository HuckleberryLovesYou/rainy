#!/usr/bin/env python3
import requests
import datetime
import argparse
import setup
import json

config = setup.Config()

def get_location_by_ip() -> tuple[float, float, str]:
    """
    Gets the current location of the user based on his public IP Address using the ipinfo.io API.
    If the User uses a VPN or Proxy, the location got, will be the location of the proxy or the VPN exit node.

    It checks if the API Call returned code 200. The latitude and longitude are rounded to 2 decimal places.

    :returns: tuple: It contains the latitude on index 0, longitude on index 1 and the city on index 2
    """
    ipinfo_api_uri = "https://ipinfo.io/json"  # gets ipinfo for current ip

    print("Fetching IP-Location-API...", end="\r")
    response = requests.get(ipinfo_api_uri)
    response.raise_for_status()

    data = response.json()
    if not data:
        raise ValueError(f"No results found for your public IP.")

    latitude_str, longitude_str = data["loc"].split(',')
    latitude = round(float(latitude_str), 2)
    longitude = round(float(longitude_str), 2)

    city = data["city"]
    return latitude, longitude, city


def get_location_by_city_name(city_name: str, country_code: str | None = None) -> tuple[float, float, str]:
    geocoding_api_uri: str = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    if country_code:
        params["countryCode"] = country_code

    print("Fetching Geocoding-API...", end="\r")
    response = requests.get(geocoding_api_uri, params=params)
    response.raise_for_status()

    data = response.json()
    results = data.get("results")
    if not results:
        raise ValueError(f"No results found for {city_name!r} in {country_code!r}.")

    latitude_str = results[0]["latitude"]
    longitude_str = results[0]["longitude"]
    latitude = round(float(latitude_str), 2)
    longitude = round(float(longitude_str), 2)

    return latitude, longitude, results[0]["name"]

def parse_weather(data: dict) -> tuple[int, str, str, float, float, float, float, float, int, bool, float, int, float, int, int]:
    """
    :param data:
    :return: tuple: It contains the weather_code (a WMO Weather interpretation (WW) code that describes the current weather (1-99) (https://open-meteo.com/en/docs))
    """
    utc_offset_seconds: int = int(data["utc_offset_seconds"])
    weather_code: int = int(data["current"]["weather_code"])
    sunrise: str = "".join(data["daily"]["sunrise"])[-5:]
    sunset: str = "".join(data["daily"]["sunset"])[-5:]
    temperature: float = float(data["current"]["temperature_2m"])
    temperature_max: float = float(data["daily"]["temperature_2m_max"][0])
    temperature_min: float = float(data["daily"]["temperature_2m_min"][0])
    apparent_temperature: float = float(data["current"]["apparent_temperature"])
    uv_index: float = float(data["daily"]["uv_index_max"][0])
    wind_speed: float = float(data["current"]["wind_speed_10m"])
    wind_direction: int = int(data["current"]["wind_direction_10m"])
    is_day: bool = bool(data["current"]["is_day"])
    humidity: int = int(data["current"]["relative_humidity_2m"])
    precipitation: float = float(data["current"]["precipitation"])
    surface_pressure: int = int(data["current"]["surface_pressure"])
    try:
        air_quality_index = int(data["current"]["us_aqi"])
    except KeyError:
        air_quality_index = None # Air Quality not requested.
    return utc_offset_seconds, weather_code, sunrise, sunset, temperature, temperature_max, temperature_min, apparent_temperature, wind_speed, wind_direction, is_day, uv_index, humidity, precipitation, surface_pressure, air_quality_index

def get_weather_by_api(latitude: float, longitude: float, wind_speed_unit: str, temperature_unit: str, precipitation_unit: str) -> dict:
    """Gets the latest weather data for the passed latitude and longitude using api.open-meteo.com.
    The API only takes latitude and longitude with 2 decimal places. The API can, but doesn't need to, take an API-Key.

    :param latitude: The latitude rounded to 2 decimal places.
    :type latitude: float
    :param longitude: The longitude rounded to 2 decimal places.
    :type longitude: float
    :param wind_speed_unit: The unit of measurement for the speed of the wind in the format needed by the API.
    :type wind_speed_unit: str
    :param temperature_unit: The unit of measurement for the temperature in the format needed by the API.
    :type temperature_unit: str
    :param precipitation_unit: The unit of measurement for the height of the precipitation in the format needed by the API.
    :type precipitation_unit: str
    """
    weather_api_uri = r"https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "sunrise,sunset,temperature_2m_max,temperature_2m_min,uv_index_max",
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,is_day,relative_humidity_2m,precipitation,surface_pressure",
        "timezone": "auto",
        "forecast_days": 1,
        "wind_speed_unit": wind_speed_unit,
        "temperature_unit": temperature_unit,
        "precipitation_unit": precipitation_unit
    }
    print("Fetching Weather-API...", end="\r")
    weather_api_response = requests.get(weather_api_uri, params=params) # https://api.open-meteo.com/v1/forecast?latitude=37.335480&longitude=-121.893028&timezone=auto&forecast_days=1
    weather_api_response.raise_for_status()
    return weather_api_response.json()


def get_air_quality_index_by_api(latitude: float, longitude: float) -> int:
    """Gets the Air Quality data for the passed latitude and longitude using air-quality-api.open-meteo.com.
    The API only takes latitude and longitude with 2 decimal places. The API can, but doesn't need to, take an API-Key.

    :param latitude: The latitude rounded to 2 decimal places.
    :type latitude: float
    :param longitude: The longitude rounded to 2 decimal places.
    :type longitude: float
    """
    air_quality_api_uri = r"https://air-quality-api.open-meteo.com/v1/air-quality"
    air_quality_api_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "us_aqi",
        "timezone": "auto",
        "forecast_days": 1,
    }
    print("Fetching Air Quality-API...", end="\r")
    air_quality_api_response = requests.get(air_quality_api_uri, params=air_quality_api_params)  # https://air-quality-api.open-meteo.com/v1/air-quality?latitude=37.335480&longitude=-121.893028&current=us_aqi&timezone=auto&forecast_days=1
    air_quality_api_response.raise_for_status()
    return int(air_quality_api_response.json()["current"]["us_aqi"])


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


def get_ascii_art(weather_code: int, is_day: bool = True) -> list[str]:
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
            r"                 "
            r"~~~~   ~~~~ ~~~  "
            r"~~~   *  ~~~~~  *"
            r"  ~~~~  ~~~ * ~~~"
            r"~~~~*   ~~~~   * "
            r"  * ~~~ ~~~~  ~~~"
            r"                 "
        ]


def get_emoji(key: str):
    """
    Gets the emoji for the passed key.
    If the key is not valid or unset, it returns an empty string.

    :param key: A key of an entry in the dictionary 'values'
    :type: key: string
    :return: An emoji that represents the key passed into it. If the key is not valid or unset, it returns an empty string.
    """
    if key == "city":
        return "\U0001F3E0"
    elif key == "weather":
        return "\U000026C5"
    elif key == "temperature":
        return "\U0001F321"
    elif key == "wind speed":
        return "\U0001F4A8"
    elif key == "wind direction":
        return "\U0001F9ED"
    elif key == "sunrise":
        return "\U0001F305"
    elif key == "sunset":
        return "\U0001F307"
    elif key == "date":
        return "\U0001F4C5"
    elif key == "time":
        return "\U000023F0"
    elif key == "precipitation":
        return "\U0001F327"
    elif key == "surface pressure":
        return "\U0001F39A"
    elif key == "humidity":
        return "\U0001F4A7"
    elif key == "uv index":
        return "\U00002600"
    else:
        return ""


def output(config, ascii_art: list[str] | None, city: str, weather: str | None, temperature_str: str, wind_speed_str: str, wind_direction_str: str | None, sunrise: str, sunset: str, current_date: str | None, current_time: str, uv_index, humidity_str, precipitation_str, surface_pressure_str, air_quality_index: int | None) -> None:
    """
    Prints the output of rainy to the terminal. It can take any amount of parameters. If no parameter is passed, the output will only be the ascii art of the current weather.
    If the amount of lines needed to display the passed parameters, it will expand the ascii art with blank lines in the same amount of characters and add the value behind it.
    
    It will not return anything in any case.

    :param ascii_art: Takes in a list of strings containing a single line of the ascii art per index.
    :type ascii_art: list
    :param city: Takes in the name of the city requested.
    :type city: str
    :param weather: Takes in the current weather.
    :type weather: str
    :param temperature_str: Takes in the current temperature already calculated with unit of measurement
    :type temperature_str: str
    :param wind_speed_str: Takes in the current wind speed already calculated with unit of measurement
    :type wind_speed_str: str
    :param wind_direction_str: Takes in the current wind direction already formated with unit of measurement
    :type wind_direction_str: str
    :param sunrise: Takes in the time of sunrise.
    :type sunrise: str
    :param sunset: Takes in the time of sunset.
    :type sunset: str
    :param current_date: Takes in the current date. Format depends on the configuration and is already passed formated.
    :type current_date: str
    :param current_time: Takes in the current time. Format depends on the configuration and is already passed formated.
    :type current_time: str
    :return: None
    """
    values: dict = {}
    if config.get("show_city"):
        values["City"] = city
    if config.get("show_weather"):
        values["Weather"] = weather
    if config.get("show_temperature"):
        values["Temperature"] = temperature_str
    if config.get("show_wind_speed"):
        values["Wind Speed"] = wind_speed_str
    if config.get("show_wind_direction"):
        values["Wind Direction"] = wind_direction_str
    if config.get("show_sunrise"):
        values["Sunrise"] = sunrise
    if config.get("show_sunset"):
        values["Sunset"] = sunset
    if config.get("show_date"):
        values["Date"] = current_date
    if config.get("show_time"):
        values["Time"] = current_time
    if config.get("show_uv_index"):
        values["UV Index"] = uv_index
    if config.get("show_humidity"):
        values["Humidity"] = humidity_str
    if config.get("show_precipitation"):
        values["Precipitation"] = precipitation_str
    if config.get("show_surface_pressure"):
        values["Surface Pressure"] = surface_pressure_str
    if config.get("show_air_quality"):
        values["Air Quality Index"] = air_quality_index

    if config.get("show_ascii_art"):
        len_diff = len(values) - len(ascii_art)
        if len_diff > 0:
            for _ in range(len_diff):
                ascii_art.append(" " * 17)

        for i, (key, value) in enumerate(values.items()):
            try:
                print(f"{ascii_art[i]}{get_emoji(key) if config.get("use_emoji") is True else "○ "} {key}: {value}")
            except IndexError:
                print(ascii_art[i])
    else:
        for key, value in values.items():
            print(f"{get_emoji(key) if config.get("use_emoji") is True else ""} {key}: {value}")

def get_api_speed_unit(unit: str) -> str:
    """
    Convert any speed unit into the API representation for the API Call.
    If an invalid unit is requested, it will return the default unit.
    Default: "kmh" (km/h)
    :param unit: This is the speed unit to get the API representation for.
    :type unit: str
    :return: API representation of the requested unit
    """
    if unit == "mph":
        return "mph"
    elif unit == "km/h":
        return "kmh"
    elif unit == "m/s":
        return "ms"
    elif unit.lower() == "knots":
        return "kn"
    else:
        print("Invalid wind speed unit. Please use supported unit. Using default.")
        return "kmh"

def get_api_temperature_unit(unit: str) -> str:
    """
    Convert any temperature unit into the API representation for the API Call.
    The API can't handle kelvin, which means it has to be converted afterward. For easy conversion, Celsius will be used for the API call.
    If an invalid unit is requested, it will return the default unit.
    Default: "celsius" (Celsius)
    :param unit: This is the temperature unit to get the API representation for.
    :type unit: str
    :return: API representation of the requested unit
    """
    if unit == "°C":
        return "celsius"
    elif unit == "°F":
        return "fahrenheit"
    elif unit == "°K":
        return "celsius"
    else:
        print("Invalid temperature unit. Please use supported unit. Using default.")
        return "celsius"

def get_api_precipitation_unit(unit: str) -> str:
    """
    Convert any precipitation unit into the API representation for the API Call.
    If an invalid unit is requested, it will return the default unit.
    Default: "mm" (Millimeters)
    :param unit: This is the precipitation unit to get the API representation for.
    :type unit: str
    :return: API representation of the requested unit
    """
    if unit == "mm" or unit == "inch":
        return unit
    else:
        print("Invalid temperature unit. Please use supported unit. Using default.")
        return "mm"


def create_parser() -> argparse.PARSER:
    parser = argparse.ArgumentParser(
        prog="Rainy",
        description="Neofetch-like, minimalistic, and customizable weather-fetching tool. Anything set using CLI-Arguments is only used for one execution of rainy. To make persistent changes edit the configuration file.",
        epilog="Example: %(prog)s --city-name Potsdam --country-code DE"
    )
    parser.add_argument("-city, --city-name", dest="city_name", help="Specify the city name to look for. For example for Potsdam the cit name would be 'Potsdam'. If not specified, looks up location by your public IP.", type=str)
    parser.add_argument("-country", "--country-code", dest="country_code", help="Specify the country code for the country to look for the specified city . A List of Country Codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements", type=str)
    parser.add_argument("--reinit", dest="reinit", action="store_true", help="This reinitializes the configuration folder at ~/.rainy. This will also delete cache and configuration.")
    parser.add_argument("--bypass-cache", dest="bypass_cache", action="store_true", help="This allows you to bypass the cache stored at ~/.rainy/cache.")
    return parser


def get_current_date(utc_offset_seconds: int, format: str) -> str:
    time_at_location = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=utc_offset_seconds)
    if format == "MM/DD/YYYY":
        return time_at_location.strftime("%m/%d/%Y")
    elif format == "DD/MM/YYYY":
        return time_at_location.strftime("%d/%m/%Y")
    elif format == "YYYY/MM/DD":
        return time_at_location.strftime("%Y/%m/%d")
    elif format == "YYYY-MM-DD":
        return time_at_location.strftime("%Y-%m-%d")
    elif format == "DD.MM.YYYY":
        return time_at_location.strftime("%d.%m.%Y")
    else:
        print(f"Invalid date format '{format}'. Please use supported date format. Using default.")
        return time_at_location.strftime("%M/%D/%Y")


def get_wind_direction(wind_direction: int) -> str:
    if wind_direction < 44:
        return "North"
    elif wind_direction < 134:
        return "East"
    elif wind_direction < 224:
        return "South"
    else:
        return "West"

def main() -> None:
    # parse CLI arguments
    parser = create_parser()
    try:
        args = parser.parse_args()
    except SystemExit:
        # Help was triggered or parsing failed
        exit()

    if args.reinit:
        config.create_cfg_folder(True)
        return None

    if args.country_code and not args.city_name:
        raise Exception("--country-code requires --city-name")
    cfg = config.load_config()

    city_name = None
    country_code = None
    if cfg.get("city_name"):
        city_name = cfg.get("city_name")
    if args.city_name:
        city_name = args.city_name

    if cfg.get("country_code"):
        country_code = cfg.get("country_code")
    if args.country_code:
        country_code = args.country_code

    if not city_name:
        latitude, longitude, city_name = get_location_by_ip()

    weather_data = None
    if not args.bypass_cache:
        weather_data = config.load_cache(city_name)
        print("Looking for cache...", end="\r")

    if weather_data is None:
        latitude, longitude, city_name = get_location_by_city_name(city_name, country_code)

        # Setup units according to configuration
        api_speed_unit = get_api_speed_unit(cfg.get("speed_unit"))
        api_temperature_unit = get_api_temperature_unit(cfg.get("temperature_unit"))
        api_precipitation_unit = get_api_precipitation_unit(cfg.get("precipitation_unit"))

        weather_data = get_weather_by_api(latitude, longitude, api_speed_unit, api_temperature_unit, api_precipitation_unit)
        if cfg.get("show_air_quality"):
            weather_data_air_quality_index = get_air_quality_index_by_api(latitude, longitude)
            weather_data["current"].update({"us_aqi": weather_data_air_quality_index})
        config.write_cache(city_name, json.dumps(weather_data))
    utc_offset_seconds, weather_code, sunrise, sunset, temperature, temperature_max, temperature_min, apparent_temperature, wind_speed, wind_direction, is_day, uv_index, humidity, precipitation, surface_pressure, air_quality_index = parse_weather(weather_data)

    # converting Celsius returned by api into kelvin
    if cfg.get("temperature_unit") == "°K":
        temperature = round(temperature + 273.2, 1)
        apparent_temperature = round(apparent_temperature + 273.2, 1)
        temperature_min = round(temperature_min + 273.2, 1)
        temperature_max = round(temperature_max + 273.2, 1)

    wind_speed_str = f"{wind_speed} {cfg.get("speed_unit")}"
    temperature_str = f"{temperature}{cfg.get("temperature_unit")}"

    # adds apparent temperature to temperature output
    if cfg.get("show_apparent_temperature"):
        temperature_str += f" feels like {apparent_temperature}{cfg.get("temperature_unit")}"
    if cfg.get("show_max_and_min_temperature"):
        temperature_str += f" ({temperature_max}{cfg.get("temperature_unit")} ↑ | {temperature_min}{cfg.get("temperature_unit")} ↓)"

    date = get_current_date(utc_offset_seconds, cfg.get("date_format"))

    time_at_location = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=utc_offset_seconds)
    if cfg.get("time_format") == "12":

        current_time = time_at_location.strftime("%I:%M:%S %p")
        sunrise_time_obj = datetime.datetime.strptime(sunrise, "%H:%M")
        sunrise = sunrise_time_obj.strftime("%I:%M %p")
        sunset_time_obj = datetime.datetime.strptime(sunset, "%H:%M")
        sunset = sunset_time_obj.strftime("%I:%M %p")
    else:
        current_time = time_at_location.strftime("%H:%M:%S")
        if cfg.get("time_format") == "24":
            print(f"Invalid time format '{cfg.get("time_format")}'. Please use supported date format. Using default.")

    humidity_str = str(humidity) + " %"
    precipitation_str = str(precipitation) + f" {cfg.get("precipitation_unit")} →1h"
    surface_pressure_str = str(surface_pressure) + " hPa"
    wind_direction_str = get_wind_direction(wind_direction)

    ascii_art = get_ascii_art(weather_code, is_day)

    weather_name = get_weather_name(weather_code)

    output(cfg, ascii_art, city_name, weather_name, temperature_str, wind_speed_str, wind_direction_str, sunrise, sunset, date, current_time, uv_index, humidity_str, precipitation_str, surface_pressure_str, air_quality_index)
    return None


if __name__ == "__main__":
    main()