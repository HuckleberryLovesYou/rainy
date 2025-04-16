#!/usr/bin/env python3

# Config
###########################################################################################################################

temperature_unit = "°C"  # Specify the unit of measurement for the temperature. Following units are valid: °C, °F, °K
wind_speed_unit = "km/h"  # Specify the unit of measurement for the speed of the wind. Following units are valid: mph, km/h, m/s, Knots
show_city = True  # Show the city name, True or False
show_weather = True  # Shows the word-representation of the weather shown in the ascii art, True or False
show_temperature = True  # Show the temperature, True or False
show_apparent_temperature = False  # Show the apparent (feels like) temperature, True or False
show_max_and_min_temperature = True  # Show the daily maximum and minimum temperature, True or False
show_wind_speed = True  # Show the wind speed, True or False
show_wind_direction = True  # Show the wind direction, True or False
show_sunrise = True  # Show the sunrise, True or False
show_sunset = True  # Show the sunset, True or False
show_date = True  # Shows the current date. True or False
date_format = "DD.MM.YYYY"  # Specify the date format. Following formats are valid: MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, YYYY-MM-DD, DD.MM.YYYY
show_time = True  # Shows the current time. True or False
time_format = 24  # Specify the time format. Following formats are valid: 12, 24
use_emoji = True
use_color = False
show_ascii_art = True

###########################################################################################################################

import requests
import datetime
import json
import emoji
from termcolor import termcolor

def get_location() -> tuple[float, float, str]:
    """Gets the current location of the user based on his public IP Address using the ipinfo.io API.
    If the User uses a VPN or Proxy, the location got, will be the location of the proxy or the VPN exit node.

    It checks if the API Call returned code 200. The latitude and longitude are rounded to 2 decimal places.

    :returns: tuple: It contains the latitude on index 0, longitude on index 1 and the city on index 2
    """
    ipinfo_api_uri = "https://ipinfo.io/json"  # gets ipinfo for current ip
    api_call = requests.get(ipinfo_api_uri)
    if not api_call.status_code == 200:
        print("Error during API Call. Check your internet connection.")
    api_response = json.loads(api_call.text)
    latitude_str, longitude_str = api_response["loc"].split(',')
    latitude = round(float(latitude_str), 2)
    longitude = round(float(longitude_str), 2)

    city = api_response["city"]
    return latitude, longitude, city


def get_weather(latitude: float, longitude: float, wind_speed_unit: str, temperature_unit: str) -> tuple[int, str, str, float, float, float, float, float, int, bool]:
    """Gets the latest weather data for the passed latitude and longitude using api.open-meteo.com.
    The API only takes latitude and longitude with 2 decimal places.

    It checks if the API Call returned code 200.

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
    api_call = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=sunrise,sunset,temperature_2m_max,temperature_2m_min&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,is_day&timezone=auto&forecast_days=1&wind_speed_unit={wind_speed_unit}&temperature_unit={temperature_unit}"
    )
    if not api_call.status_code == 200:
        if api_call.status_code == 400:
            print("Error during API Call. URL parameter is not correctly specified")
        else:
            print("Error during API Call. Check your internet connection.")
    api_response = json.loads(api_call.text)
    weather_code: int = int(api_response["current"]["weather_code"])
    sunrise: str = "".join(api_response["daily"]["sunrise"])[-5:]
    sunset: str = "".join(api_response["daily"]["sunset"])[-5:]
    temperature: float = float(api_response["current"]["temperature_2m"])
    temperature_max: float = float(api_response["daily"]["temperature_2m_max"][0])
    temperature_min: float = float(api_response["daily"]["temperature_2m_min"][0])
    apparent_temperature: float = float(api_response["current"]["apparent_temperature"])
    wind_speed: float = float(api_response["current"]["wind_speed_10m"])
    wind_direction: int = int(api_response["current"]["wind_direction_10m"])
    is_day: bool = bool(api_response["current"]["is_day"])
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
                r"         _.._  ",
                r"       .' .-'` ",
                r"      /  /     ",
                r"      |  |     ",
                r"      \  \     ",
                r"       '._'-._ ",
                r"          ```   "
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


def print_output(ascii_art: list[str] | None, city: str, weather: str | None, temperature_str: str, wind_speed_str: str, wind_direction_str: str | None, sunrise: str, sunset: str, current_date: str | None, current_time: str) -> None:
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
    if show_city:
        values["city"] = city
    if show_weather and weather is not None:
        values["weather"] = weather
    if show_temperature:
        values["temperature"] = temperature_str
    if show_wind_speed:
        values["wind speed"] = wind_speed_str
    if show_wind_direction:
        values["wind direction"] = wind_direction_str
    if show_sunrise:
        values["sunrise"] = sunrise
    if show_sunset:
        values["sunset"] = sunset
    if show_date:
        values["date"] = current_date
    if show_time:
        values["time"] = current_time

    if show_ascii_art:
        len_diff = len(values) - len(ascii_art)
        if len_diff > 0:
            for _ in range(len_diff):
                ascii_art.append(" " * len(ascii_art[0]))

        for i, (key, value) in enumerate(values.items()):
            try:
                if use_color:
                    print(ascii_art[i], end="")
                    termcolor.cprint(f"{get_emoji(key) if use_emoji is True else ""} {key.capitalize()}: {value}", f"{get_color(key)}")
                else:
                    print(f"{ascii_art[i]}{get_emoji(key) if use_emoji is True else ""} {key.capitalize()}: {value}")
            except IndexError:
                print(ascii_art[i])
    else:
        for key, value in values.items():
            if use_color:
                termcolor.cprint(f"{get_emoji(key) if use_emoji is True else ""} {key.capitalize()}: {value}", f"{get_color(key)}")
            else:
                print(f"{get_emoji(key) if use_emoji is True else ""} {key.capitalize()}: {value}")


def main() -> None:
    # Setup units according to configuration
    if wind_speed_unit == "mph":
        api_wind_speed_unit = "mph"
    elif wind_speed_unit == "km/h":
        api_wind_speed_unit = "kmh"
    elif wind_speed_unit == "m/s":
        api_wind_speed_unit = "ms"
    elif wind_speed_unit.lower() == "knots":
        api_wind_speed_unit = "kn"
    else:
        print("Invalid wind speed unit. Please use supported unit. Using default.")
        api_wind_speed_unit = "kmh"

    if temperature_unit == "°C":
        api_temperature_unit = "celsius"
    elif temperature_unit == "°F":
        api_temperature_unit = "fahrenheit"
    elif temperature_unit == "°K":
        api_temperature_unit = "celsius"
    else:
        print("Invalid temperature unit. Please use supported unit. Using default.")
        api_temperature_unit = "celsius"

    latitude, longitude, city = get_location()
    weather_code, sunrise, sunset, temperature, temperature_max, temperature_min, apparent_temperature, wind_speed, wind_direction, is_day = get_weather(latitude, longitude, api_wind_speed_unit, api_temperature_unit)

    # converting celsius returned by api into kelvin
    if temperature_unit == "°K":
        temperature += 273.2
        apparent_temperature += 273.2
        temperature_min += 273.2
        temperature_max += 273.2

    wind_speed_str = f"{wind_speed} {wind_speed_unit}"
    temperature_str = f"{temperature}{temperature_unit}"

    # adds apparent temperature to temperature output
    if show_apparent_temperature:
        temperature_str += f" feels like {apparent_temperature}{temperature_unit}"
    if show_max_and_min_temperature:
        temperature_str += f" ({temperature_max}{temperature_unit} ↑ | {temperature_min}{temperature_unit} ↓)"

    if show_date:
        if date_format == "MM/DD/YYYY":
            current_date = datetime.datetime.now().strftime("%m/%d/%Y")
        elif date_format == "DD/MM/YYYY":
            current_date = datetime.datetime.now().strftime("%d/%m/%Y")
        elif date_format == "YYYY/MM/DD":
            current_date = datetime.datetime.now().strftime("%Y/%m/%d")
        elif date_format == "YYYY-MM-DD":
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        elif date_format == "DD.MM.YYYY":
            current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        else:
            print("Invalid date format. Please use supported date format. Using default.")
            current_date = datetime.datetime.now().strftime("%M/%D/%Y")
    else:
        current_date = None

    if time_format == 12:
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

        sunrise_time_obj = datetime.datetime.strptime(sunrise, "%H:%M")
        sunrise = sunrise_time_obj.strftime("%I:%M %p")
        sunset_time_obj = datetime.datetime.strptime(sunset, "%H:%M")
        sunset = sunset_time_obj.strftime("%I:%M %p")

    elif time_format == 24:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
    else:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("Invalid time format. Please use supported date format. Using default.")

    if show_wind_direction:
        if wind_direction < 44:
            wind_direction_str: str = "N"
        elif wind_direction < 134:
            wind_direction_str: str = "E"
        elif wind_direction < 224:
            wind_direction_str: str = "S"
        else:
            wind_direction_str: str = "N"
    else:
        wind_direction_str: None = None

    if show_ascii_art:
        ascii_art = get_ascii_art(weather_code, is_day)
    else:
        ascii_art = None

    if show_weather:
        weather = get_weather_name(weather_code)
    else:
        weather = None

    print_output(ascii_art, city, weather, temperature_str, wind_speed_str, wind_direction_str, sunrise, sunset, current_date, current_time)


if __name__ == "__main__":
    main()