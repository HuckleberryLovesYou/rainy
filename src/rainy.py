#!/usr/bin/env python3

# Config

###########################################################################################################################


temperature_unit = "°C"  # Specify the unit of measurement for the temperature. Following units are valid: °C, °F, °K
wind_speed_unit = "km/h" # Specify the unit of measurement for the speed of the wind. Following units are valid: mph, km/h, m/s, Knots
show_city = True  # Show the city name in information, True or False
show_date = True # Shows the current date. True or False
date_format = "DD.MM.YYYY" # Specify the date format. Following formats are valid: MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, YYYY-MM-DD, DD.MM.YYYY
show_time = True # Shows the current time. True or False

###########################################################################################################################

import requests
import datetime
import json

#def get_time_offset() -> int:
#    return int(str(datetime.datetime.now(datetime.timezone.utc).astimezone().utcoffset()).split(":")[0])

def get_location() -> tuple[float, float, str]:
    ipinfo_api_uri = "https://ipinfo.io/json" # gets ipinfo for current ip
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
    api_call = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=sunrise,sunset&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto&forecast_days=1&wind_speed_unit={wind_speed_unit}&temperature_unit={temperature_unit}"
    )
    if not api_call.status_code == 200:
        print("Error during API Call. Check your internet connection.")
    api_response = json.loads(api_call.text)
    weather_code: int = int(api_response["current"]["weather_code"])
    sunrise: str = "".join(api_response["daily"]["sunrise"])[-5:]
    sunset: str = "".join(api_response["daily"]["sunset"])[-5:]
    temperature: float = float(api_response["current"]["temperature_2m"])
    apparent_temperature: float = float(api_response["current"]["apparent_temperature"])
    wind_speed: float = float(api_response["current"]["wind_speed_10m"])
    return weather_code, sunrise, sunset, temperature, apparent_temperature, wind_speed

def print_output(weather_code: int, city: str, temperature_str: str, wind_speed_str: str, sunrise: str, sunset: str, current_date: str | None, current_time: str) -> None:
    if weather_code == 0:
        output = (
            [
                r"               " + "City: " + city,
                r"     \   /     " + "Weather: clear",
                r"      .-.      " + "Temperature: " + temperature_str,
                r"   ‒ (   ) ‒   " + "Wind speed: " + wind_speed_str,
                r"      `-᾿      " + "Sunrise: " + sunrise,
                r"     /   \     " + "Sunset: " + sunset,
                r"               " + "Date: " + current_date if show_date else "",
                r"               " + "Time: " + current_time if show_time else "",
            ]
            if show_city
            else [
                r"               ",
                r"     \   /     " + "Weather: clear",
                r"      .-.      " + "Temperature: " + temperature_str,
                r"   ‒ (   ) ‒   " + "Wind speed: " + wind_speed_str,
                r"      `-᾿      " + "Sunrise: " + sunrise,
                r"     /   \     " + "Sunset: " + sunset,
                r"               " + "Date: " + current_date if show_date else "",
                r"               " + "Time: " + current_time if show_time else "",
            ]
        )
    elif weather_code in [1, 2, 3]:
        output = (
            [
                r"                 " + "City: " + city if show_date else "",
                r"       .--.      " + "Weather: cloudy",
                r"    .-(    ).    " + "Temprature: " + temperature_str,
                r"   (___.__)__)   " + "Wind speed: " + wind_speed_str,
                r"                 " + "Sunrise: " + sunrise,
                r"                 " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
            if show_city
            else [
                r"                 " + "Weather: cloudy",
                r"       .--.      " + "Temprature: " + temperature_str,
                r"    .-(    ).    " + "Wind speed: " + wind_speed_str,
                r"   (___.__)__)   " + "Sunrise: " + sunrise,
                r"                 " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
        )
    elif weather_code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        output = (
            [
                r"                 " + "City: " + city,
                r"       .--.      " + "Weather: rainy",
                r"    .-(    ).    " + "Temprature: " + temperature_str,
                r"   (___.__)__)   " + "Wind speed: " + wind_speed_str,
                r"    ʻ‚ʻ‚ʻ‚ʻ‚ʻ    " + "Sunrise: " + sunrise,
                r"                 " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
            if show_city
            else [
                r"                 " + "Weather: rainy",
                r"       .--.      " + "Temprature: " + temperature_str,
                r"    .-(    ).    " + "Wind speed: " + wind_speed_str,
                r"   (___.__)__)   " + "Sunrise: " + sunrise,
                r"    ʻ‚ʻ‚ʻ‚ʻ‚ʻ    " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
        )
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        output = (
            [
                r"                 " + "City: " + city,
                r"       .--.      " + "Weather: snowy",
                r"    .-(    ).    " + "Temprature: " + temperature_str,
                r"   (___.__)__)   " + "Wind speed: " + wind_speed_str,
                r"    * * * * *    " + "Sunrise: " + sunrise,
                r"                 " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
            if show_city
            else [
                r"                 " + "Weather: snowy",
                r"       .--.      " + "Temprature: " + temperature_str,
                r"    .-(    ).    " + "Wind speed: " + wind_speed_str,
                r"   (___.__)__)   " + "Sunrise: " + sunrise,
                r"    * * * * *    " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
        )
    elif weather_code in [95, 96, 99]:
        output = (
            [
                r"                 " + "City: " + city,
                r"       .--.      " + "Weather: stormy",
                r"    .-(    ).    " + "Temprature: " + temperature_str,
                r"   (___.__)__)   " + "Wind speed: " + wind_speed_str,
                r"        /_       " + "Sunrise: " + sunrise,
                r"         /       " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
            if show_city
            else [
                r"       .--.      " + "Weather: stormy",
                r"    .-(    ).    " + "Temprature: " + temperature_str,
                r"   (___.__)__)   " + "Wind speed: " + wind_speed_str,
                r"        /_       " + "Sunrise: " + sunrise,
                r"         /       " + "Sunset: " + sunset,
                r"                 " + "Date: " + current_date if show_date else "",
                r"                 " + "Time: " + current_time if show_time else "",
            ]
        )
    else:
        output = (
            [
                r"~~~~   ~~~~ ~~~   * ~~~~~~~ " + "City: " + city,
                r"~~~   *  ~~~~~  * ~~~~  ~~~~" + "Weather: foggy",
                r"  ~~~~  ~~~ * ~~~~~ ~~~~   ~" + "Temprature: " + temperature_str,
                r"~~~~*   ~~~~   * ~~~~   ~~~~" + "Wind speed: " + wind_speed_str,
                r"  * ~~~ ~~~~  ~~~~~  * ~~~~ " + "Sunrise: " + sunrise,
                r"~~~~  * ~~~~ ~~~   ~~~~~~~~ " + "Sunset: " + sunset,
                r"                            " + "Date: " + current_date if show_date else "",
                r"                            " + "Time: " + current_time if show_time else "",
            ]
            if show_city
            else [
                r"  * ~~~ ~~~~  ~~~~~  * ~~~~ " + "Weather: foggy",
                r"~~~   *  ~~~~~  * ~~~~  ~~~~" + "Temprature: " + temperature_str,
                r"  ~~~~  ~~~ * ~~~~~ ~~~~   ~" + "Wind speed: " + wind_speed_str,
                r"~~~~*   ~~~~   * ~~~~   ~~~~" + "Sunrise: " + sunrise,
                r"  * ~~~ ~~~~  ~~~~~  * ~~~~ " + "Sunset: " + sunset,
                r"~~~~  * ~~~~ ~~~   ~~~~~~~~ " + "Date: " + current_date if show_date else "",
                r"                            " + "Time: " + current_time if show_time else "",
            ]
        )

    print(*output, sep="\n")


def main() -> None:
    # Setup units according to configuration
    global temperature_unit
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


    current_time = datetime.datetime.now().strftime("%H:%M:%S")


    print_output(weather_code, city, temperature_str, wind_speed_str, sunrise, sunset, current_date, current_time)

if __name__ == "__main__":
    main()
