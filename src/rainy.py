#!/usr/bin/env python3

# Config
###########################################################################################################################

temperature_unit = "°C"  # Specify the unit of measurement for the temperature. Following units are valid: °C, °F, °K
wind_speed_unit = "km/h"  # Specify the unit of measurement for the speed of the wind. Following units are valid: mph, km/h, m/s, Knots
show_city = True  # Show the city name, True or False
show_weather = True  # Shows the word-representation of the weather shown in the ascii art, True or False
show_temperature = True  # Show the temperature, True or False
show_wind_speed = True  # Show the wind speed, True or False
show_sunrise = True  # Show the sunrise, True or False
show_sunset = True  # Show the sunset, True or False
show_date = True  # Shows the current date. True or False
date_format = "DD.MM.YYYY"  # Specify the date format. Following formats are valid: MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, YYYY-MM-DD, DD.MM.YYYY
show_time = True  # Shows the current time. True or False
time_format = 24  # Specify the time format. Following formats are valid: 12, 24

###########################################################################################################################

import requests
import datetime
import json

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


def get_weather(latitude: float, longitude: float, wind_speed_unit: str, temperature_unit: str) -> tuple[int, str, str, float, float, float]:
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

    :returns: tuple: It contains the weather_code (a WMO Weather interpretation (WW) code that describes the current weather (1-99) (https://open-meteo.com/en/docs)) on index 0 as an int,
    the sunrise on index 1 as a str, the sunset on index 2 as a str, the temperature on index 3 as a float, the apparent_temperature on index 4 as a float, the wind_speed on index 5 as a float.
    """
    api_call = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=sunrise,sunset&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto&forecast_days=1&wind_speed_unit={wind_speed_unit}&temperature_unit={temperature_unit}"
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
    apparent_temperature: float = float(api_response["current"]["apparent_temperature"])
    wind_speed: float = float(api_response["current"]["wind_speed_10m"])
    return weather_code, sunrise, sunset, temperature, apparent_temperature, wind_speed


def get_ascii_art_and_weather_name(weather_code: int) -> tuple[list[str], str]:
    """Gets the ascii art for the passed weather_code and returns it in a list as well as the friendly name of the current weather.

    :param weather_code: The code of the current weather returned by the API (a WMO Weather interpretation code (WW) 1-99. Further Information here: https://open-meteo.com/en/docs).
    :type weather_code: int

    :returns: tuple: It contains a list of the ascii art, where on each index there's a single line of the ascii art and the friendly name of the current weather, since get_weather() returns the weather code.
    """
    if weather_code == 0:
        return [
            r"               ",
            r"     \   /     ",
            r"      .-.      ",
            r"   ‒ (   ) ‒   ",
            r"      `-᾿      ",
            r"     /   \     ",
            r"               "
        ], "clear"
    elif weather_code in [1, 2, 3]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"                 ",
            r"                 ",
            r"                 ",
        ], "cloudy"
    elif weather_code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"    ʻ‚ʻ‚ʻ‚ʻ‚ʻ    ",
            r"                 ",
            r"                 ",
        ], "rainy"
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"    * * * * *    ",
            r"                 ",
            r"                 ",
        ], "snowy"
    elif weather_code in [95, 96, 99]:
        return [
            r"                 ",
            r"       .--.      ",
            r"    .-(    ).    ",
            r"   (___.__)__)   ",
            r"        /_       ",
            r"         /       ",
            r"                 ",
        ], "thundery"
    else:
        return [
            r"~~~~ * ~~~~ ~~~   ~~~~~~ * ~"
            r"~~~~   ~~~~ ~~~   * ~~~~~~~ "
            r"~~~   *  ~~~~~  * ~~~~  ~~~~"
            r"  ~~~~  ~~~ * ~~~~~ ~~~~   ~"
            r"~~~~*   ~~~~   * ~~~~   ~~~~"
            r"  * ~~~ ~~~~  ~~~~~  * ~~~~ "
            r"~~~~  * ~~~~ ~~~   ~~~~~~~~ "
        ], "foggy"


def print_output(ascii_art: list[str], city: str, weather: str, temperature_str: str, wind_speed_str: str, sunrise: str, sunset: str, current_date: str, current_time: str) -> None:
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
    values: list[str] = []
    if show_city:
        values.append(city)
    if show_weather:
        values.append(f"Weather: {weather}")
    if show_temperature:
        values.append(temperature_str)
    if show_wind_speed:
        values.append(wind_speed_str)
    if show_sunrise:
        values.append(sunrise)
    if show_sunset:
        values.append(sunset)
    if show_date:
        values.append(current_date)
    if show_time:
        values.append(current_time)

    len_diff = len(values) - len(ascii_art)
    if len_diff > 0:
        for _ in range(len_diff):
            ascii_art.append(" " * len(ascii_art[0]))

    for i, ascii_art_line in enumerate(ascii_art):
        try:
            print(f"{ascii_art_line}{values[i]}")
        except IndexError:
            print(ascii_art_line)


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
    weather_code, sunrise, sunset, temperature, apparent_temperature, wind_speed = get_weather(latitude, longitude, api_wind_speed_unit, api_temperature_unit)

    # converting celsius returned by api into kelvin
    if temperature_unit == "°K":
        temperature += 273.2

    wind_speed_str = f"{wind_speed} {wind_speed_unit}"
    temperature_str = f"{temperature} {temperature_unit}"

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
        print("Invalid time format. Please use supported date format. Using default.")

    ascii_art, weather = get_ascii_art_and_weather_name(weather_code)
    print_output(ascii_art, city, weather, temperature_str, wind_speed_str, sunrise, sunset, current_date, current_time)


if __name__ == "__main__":
    main()
