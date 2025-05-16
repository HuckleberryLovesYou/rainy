#!/usr/bin/env python3

import os
import requests
import datetime
import emoji
import termcolor
import argparse
import configparser

def load_config():
    parser = configparser.ConfigParser()
    parser.read(os.path.join(os.path.dirname(__file__), "rainy.conf.ini"))

    # load configuration
    cfg = {
        # Location
        "city_name": parser.get("Location", "city_name"),
        "country_code": parser.get("Location", "country_code"),

        # Units
        "temperature_unit": "°" + parser.get("Units", "temperature_unit"),
        "speed_unit": parser.get("Units", "speed_unit"),

        # Formats
        "date_format": parser.get("Formats", "date_format"),
        "time_format": parser.getint("Formats", "time_format"),

        # What to show
        "show_city": parser.getboolean("Show", "show_city"),
        "show_weather": parser.getboolean("Show", "show_weather"),
        "show_temperature": parser.getboolean("Show", "show_temperature"),
        "show_apparent_temperature": parser.getboolean("Show", "show_apparent_temperature"),
        "show_max_and_min_temperature": parser.getboolean("Show", "show_max_and_min_temperature"),
        "show_wind_speed": parser.getboolean("Show", "show_wind_speed"),
        "show_wind_direction": parser.getboolean("Show", "show_wind_direction"),
        "show_sunrise": parser.getboolean("Show", "show_sunrise"),
        "show_sunset": parser.getboolean("Show", "show_sunset"),
        "show_date": parser.getboolean("Show", "show_date"),
        "show_time": parser.getboolean("Show", "show_time"),

        # Output options
        "use_emoji": parser.getboolean("Output", "use_emoji"),
        "use_color": parser.getboolean("Output", "use_color"),
        "show_ascii_art": parser.getboolean("Output", "show_ascii_art"),
    }
    return cfg

def get_location_by_ip() -> tuple[float, float, str]:
    """
    Gets the current location of the user based on his public IP Address using the ipinfo.io API.
    If the User uses a VPN or Proxy, the location got, will be the location of the proxy or the VPN exit node.

    It checks if the API Call returned code 200. The latitude and longitude are rounded to 2 decimal places.

    :returns: tuple: It contains the latitude on index 0, longitude on index 1 and the city on index 2
    """
    ipinfo_api_uri = "https://ipinfo.io/json"  # gets ipinfo for current ip
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

    response = requests.get(geocoding_api_uri, params=params)
    response.raise_for_status()

    data = response.json()
    results = data.get("results")
    if not results:
        raise ValueError(f"No results found for {city_name!r} ({country_code}).")

    latitude_str = results[0]["latitude"]
    longitude_str = results[0]["longitude"]
    latitude = round(float(latitude_str), 2)
    longitude = round(float(longitude_str), 2)

    return latitude, longitude, results[0]["name"]


def get_weather(latitude: float, longitude: float, wind_speed_unit: str, temperature_unit: str) -> tuple[int, str, str, float, float, float, float, float, int, bool]:
    """Gets the latest weather data for the passed latitude and longitude using api.open-meteo.com.
    The API only takes latitude and longitude with 2 decimal places.

    :param latitude: The latitude rounded to 2 decimal places.
    :type latitude: float
    :param longitude: The longitude rounded to 2 decimal places.
    :type longitude: float
    :param wind_speed_unit: The unit of measurement for the speed of the wind in the format needed by the API.
    :type wind_speed_unit: str
    :param temperature_unit: The unit of measurement for the temperature in the format needed by the API.
    :type temperature_unit: str

    :returns: tuple: It contains the weather_code (a WMO Weather interpretation (WW) code that describes the current weather (1-99) (https://open-meteo.com/en/docs))
    """
    forecast_api_uri = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "sunrise,sunset,temperature_2m_max,temperature_2m_min",
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,is_day",
        "timezone": "auto",
        "forecast_days": 1,
        "wind_speed_unit": wind_speed_unit,
        "temperature_unit": temperature_unit
    }
    response = requests.get(forecast_api_uri, params=params)
    response.raise_for_status()

    data = response.json()
    weather_code: int = int(data["current"]["weather_code"])
    sunrise: str = "".join(data["daily"]["sunrise"])[-5:]
    sunset: str = "".join(data["daily"]["sunset"])[-5:]
    temperature: float = float(data["current"]["temperature_2m"])
    temperature_max: float = float(data["daily"]["temperature_2m_max"][0])
    temperature_min: float = float(data["daily"]["temperature_2m_min"][0])
    apparent_temperature: float = float(data["current"]["apparent_temperature"])
    wind_speed: float = float(data["current"]["wind_speed_10m"])
    wind_direction: int = int(data["current"]["wind_direction_10m"])
    is_day: bool = bool(data["current"]["is_day"])
    return weather_code, sunrise, sunset, temperature, temperature_max, temperature_min, apparent_temperature, wind_speed, wind_direction, is_day

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


def get_ascii_art(weather_code: int, is_day: bool) -> list[str]:
    """Gets the ascii art for the passed weather_code and returns it in a list as well as the friendly name of the current weather.

    :param weather_code: The code of the current weather returned by the API (a WMO Weather interpretation code (WW) 1-99. Further Information here: https://open-meteo.com/en/docs).
    :type weather_code: int

    :returns: tuple: It contains a list of the ascii art, where on each index there's a single line of the ascii art.
    """
    if weather_code == 0:
        if is_day:
            return [
                r"               ",
                r"     \   /     ",
                r"      .-.      ",
                r"   ‒ (   ) ‒   ",
                r"      `-᾿      ",
                r"     /   \     ",
                r"               "
            ]
        else:
            return [
                r"               ",
                r"       _.._    ",
                r"     .' .-'`   ",
                r"    /  /       ",
                r"    |  |       ",
                r"    \  \       ",
                r"     '._'-._   ",
                r"        ```    "
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
            r"                            "
            r"~~~~   ~~~~ ~~~   * ~~~~~~~ "
            r"~~~   *  ~~~~~  * ~~~~  ~~~~"
            r"  ~~~~  ~~~ * ~~~~~ ~~~~   ~"
            r"~~~~*   ~~~~   * ~~~~   ~~~~"
            r"  * ~~~ ~~~~  ~~~~~  * ~~~~ "
            r"                            "
        ]


def get_emoji(key: str) -> emoji:
    """
    Gets the emoji for the passed key.
    If the key is not valid or unset, it returns an empty string.

    :param key: A key of an entry in the dictionary 'values'
    :type: key: string
    :return: An emoji that represents the key passed into it. If the key is not valid or unset, it returns an empty string.
    """
    if key == "city":
        return emoji.emojize(":derelict_house:")
    elif key == "weather":
        return emoji.emojize(":sun_behind_rain_cloud:")
    elif key == "temperature":
        return emoji.emojize(":thermometer:")
    elif key == "wind speed":
        return emoji.emojize(":dashing_away:")
    elif key == "wind direction":
        return emoji.emojize(":compass:")
    elif key == "sunrise":
        return emoji.emojize(":sunrise:")
    elif key == "sunset":
        return emoji.emojize(":sunset:")
    elif key == "date":
        return emoji.emojize(":calendar:")
    elif key == "time":
        return emoji.emojize(":alarm_clock:")
    else:
        return ""

def get_color(key: str) -> str:
    """
    Gets the color for the passed key.
    If the key is not valid or unset, it returns the color 'white'.

    :param key: A key of an entry in the dictionary 'values'
    :type: key: string
    :return: A string containing the color for the termcolor output depending on the passed key. If the key is not valid or unset, it returns the color 'white'.
    """
    if key == "city":
        return "blue"
    elif key == "weather":
        return "cyan"
    elif key == "temperature":
        return "red"
    elif key == "wind speed":
        return "green"
    elif key == "wind direction":
        return "yellow"
    elif key == "sunrise":
        return "magenta"
    elif key == "sunset":
        return "magenta"
    else:
        return "white"


def output(config, ascii_art: list[str] | None, city: str, weather: str | None, temperature_str: str, wind_speed_str: str, wind_direction_str: str | None, sunrise: str, sunset: str, current_date: str | None, current_time: str) -> None:
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
        values["city"] = city
    if config.get("show_weather"):
        values["weather"] = weather
    if config.get("show_temperature"):
        values["temperature"] = temperature_str
    if config.get("show_wind_speed"):
        values["wind speed"] = wind_speed_str
    if config.get("show_wind_direction"):
        values["wind direction"] = wind_direction_str
    if config.get("show_sunrise"):
        values["sunrise"] = sunrise
    if config.get("show_sunset"):
        values["sunset"] = sunset
    if config.get("show_date"):
        values["date"] = current_date
    if config.get("show_time"):
        values["time"] = current_time

    if config.get("show_ascii_art"):
        len_diff = len(values) - len(ascii_art)
        if len_diff > 0:
            for _ in range(len_diff):
                ascii_art.append(" " * len(ascii_art[0]))

        for i, (key, value) in enumerate(values.items()):
            try:
                if config.get("use_color"):
                    print(ascii_art[i], end="")
                    termcolor.cprint(f"{get_emoji(key) if config.get("use_emoji") is True else ""} {key.capitalize()}: {value}", f"{get_color(key)}")
                else:
                    print(f"{ascii_art[i]}{get_emoji(key) if config.get("use_emoji") is True else ""} {key.capitalize()}: {value}")
            except IndexError:
                print(ascii_art[i])
    else:
        for key, value in values.items():
            if config.get("use_color"):
                termcolor.cprint(f"{get_emoji(key) if config.get("use_emoji") is True else ""} {key.capitalize()}: {value}", f"{get_color(key)}")
            else:
                print(f"{get_emoji(key) if config.get("use_emoji") is True else ""} {key.capitalize()}: {value}")

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


def create_parser() -> argparse.PARSER:
    parser = argparse.ArgumentParser(
        prog="Rainy",
        description="Neofetch-like, minimalistic, and customizable weather-fetching tool.",
        epilog="Example: %(prog)s --city-name Potsdam --country-code DE"
    )
    parser.add_argument("-city, --city-name", dest="city_name", help="Specify the city name to look for. For example for Potsdam the cit name would be 'Potsdam'. If not specified, looks up location by your public IP.", type=str)
    parser.add_argument("-country", "--country-code", dest="country_code", help="Specify the country code for the country to look for the specified city . A List of Country Codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements", type=str)

    return parser


def get_current_date(format: str):
    if format == "MM/DD/YYYY":
        return datetime.datetime.now().strftime("%m/%d/%Y")
    elif format == "DD/MM/YYYY":
        return datetime.datetime.now().strftime("%d/%m/%Y")
    elif format == "YYYY/MM/DD":
        format = datetime.datetime.now().strftime("%Y/%m/%d")
    elif format == "YYYY-MM-DD":
        return datetime.datetime.now().strftime("%Y-%m-%d")
    elif format == "DD.MM.YYYY":
        return datetime.datetime.now().strftime("%d.%m.%Y")
    else:
        print("Invalid date format. Please use supported date format. Using default.")
        return datetime.datetime.now().strftime("%M/%D/%Y")


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

    if args.country_code and not args.city_name:
        raise Exception("--country-code requires --city-name")

    config = load_config()

    # Setup units according to configuration
    api_speed_unit = get_api_speed_unit(config.get("speed_unit"))
    api_temperature_unit = get_api_temperature_unit(config.get("temperature_unit"))


    if args.city_name:
        if args.country_code:
            latitude, longitude, city = get_location_by_city_name(args.city_name, args.country_code)
        else:
            latitude, longitude, city = get_location_by_city_name(args.city_name)
    elif config.get("city_name"):
        if config.get("country_code"):
            latitude, longitude, city = get_location_by_city_name(config.get("city_name"), config.get("country_code"))
        else:
            latitude, longitude, city = get_location_by_city_name(config.get("city_name"))
    else:
        latitude, longitude, city = get_location_by_ip()

    weather_code, sunrise, sunset, temperature, temperature_max, temperature_min, apparent_temperature, wind_speed, wind_direction, is_day = get_weather(latitude, longitude, api_speed_unit, api_temperature_unit)

    # converting Celsius returned by api into kelvin
    if config.get("temperature_unit") == "°K":
        temperature = round(temperature + 273.2, 1)
        apparent_temperature = round(apparent_temperature + 273.2, 1)
        temperature_min = round(temperature_min + 273.2, 1)
        temperature_max = round(temperature_max + 273.2, 1)

    wind_speed_str = f"{wind_speed} {config.get("speed_unit")}"
    temperature_str = f"{temperature}{config.get("temperature_unit")}"

    # adds apparent temperature to temperature output
    if config.get("show_apparent_temperature"):
        temperature_str += f" feels like {apparent_temperature}{config.get("temperature_unit")}"
    if config.get("show_max_and_min_temperature"):
        temperature_str += f" ({temperature_max}{config.get("temperature_unit")} ↑ | {temperature_min}{config.get("temperature_unit")} ↓)"

    date = get_current_date(config.get("date_format"))

    if config.get("time_format") == 12:
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

        sunrise_time_obj = datetime.datetime.strptime(sunrise, "%H:%M")
        sunrise = sunrise_time_obj.strftime("%I:%M %p")
        sunset_time_obj = datetime.datetime.strptime(sunset, "%H:%M")
        sunset = sunset_time_obj.strftime("%I:%M %p")
    else:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        if config.get("time_format") == 24:
            print("Invalid time format. Please use supported date format. Using default.")

    wind_direction_str = get_wind_direction(wind_direction)

    ascii_art = get_ascii_art(weather_code, is_day)

    weather = get_weather_name(weather_code)

    output(config, ascii_art, city, weather, temperature_str, wind_speed_str, wind_direction_str, sunrise, sunset, date, current_time)


if __name__ == "__main__":
    main()