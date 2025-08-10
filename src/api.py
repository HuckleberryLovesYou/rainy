import requests
from exceptions import APIError


class API:
    def __init__(self):
        self.apis: dict = {"ipinfo": [r"https://ipinfo.io/json", "Fetching IP-Location-API..."],
                           "geocoding": [r"https://geocoding-api.open-meteo.com/v1/search", "Fetching Geocoding-API..."],
                           "forecast": [r"https://api.open-meteo.com/v1/forecast", "Fetching Weather-API..."],
                           "air_quality": [r"https://air-quality-api.open-meteo.com/v1/air-quality", "Fetching Air Quality-API..."]}

    def api_call(self, api: str, params: dict = None):
        """
        This function makes API Calls, prints the process of the API Call, checks if API Call was successful and returns the response data as json.
        It also allows to set parameters for the API Call. If no parameters are set, the API will be called without any parameters.
        If the API Call fails, it will raise the according HTTP error.
        Available APIs: ipinfo, geocoding, forecast, air_quality


        :param api: Allows to select the API to call. Only the api listed above are available
        :param params: Optinal - Allows to set parameters for the API Call
        :return: Returns the json-encoded response.
        """
        api_info = self.apis.get(api)
        if not api_info:
            raise Exception(f"No Information found for api {api!r} in self.api_info.")
        print(api_info[1] + (" " * 30), end="\n")
        if not params:
            params = {}

        response = requests.get(api_info[0], params=params)
        response.raise_for_status()

        return response.json()

    def get_location_by_ip(self) -> tuple[float, float, str]:
        """
        Gets the current location of the user based on his public IP Address using the ipinfo.io API.
        If the User uses a VPN or Proxy, the location got, will be the location of the proxy or the VPN exit node.
        The latitude and longitude are rounded to 2 decimal places.

        :returns: tuple: It contains the latitude on index 0, longitude on index 1 and the city on index 2
        """

        data = self.api_call("ipinfo")
        if not data:
            raise ValueError("No results found for your public IP.")

        latitude_str, longitude_str = data["loc"].split(',')
        latitude = round(float(latitude_str), 2)
        longitude = round(float(longitude_str), 2)

        city = data["city"]
        return latitude, longitude, city

    def get_location_by_city_name(self, city_name: str, country_code: str | None = None) -> tuple[float, float, str]:
        """
        Gets the longitude and latitude for a given city name. If a country code is given, it will only look for the city name within the corresponding country for the given country code.
        If the city is not found (or not found within the given country) it raises an Exception. If the API returned an error, it raises an Exception with the error reason.

        :param city_name: The City name to look up
        :param country_code: The country code of the country in which the city is.
        :return: It returns the latitude and longitude rounded to 2 decimal places and the correctly capitalized returned city name.
        """

        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        if country_code:
            params["countryCode"] = country_code

        data = self.api_call("geocoding", params=params)
        results = data.get("results")

        if data.get("error"):
            raise Exception(f"Error. Reason: {data.get("reason")}")
        elif not results:
            raise Exception(f"No results found for {city_name!r} in {country_code!r}.")

        latitude_str = results[0]["latitude"]
        longitude_str = results[0]["longitude"]
        latitude = round(float(latitude_str), 2)
        longitude = round(float(longitude_str), 2)
        city_name_out = results[0]["name"]

        return latitude, longitude, city_name_out

    def get_weather_forecast(self, latitude: float, longitude: float, wind_speed_unit: str, temperature_unit: str, precipitation_unit: str) -> dict:
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
        :param precipitation_unit: The unit of measurement for the height of the precipitation in the format needed by the API.
        :type precipitation_unit: str
        """

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

        data = self.api_call("forecast", params=params)

        return data

    def get_air_quality(self, latitude: float, longitude: float) -> int:
        """
        Gets the Air Quality data for the passed latitude and longitude using air-quality-api.open-meteo.com.
        The API only takes latitude and longitude with 2 decimal places. The API can, but doesn't need to, take an API-Key.

        :param latitude: The latitude rounded to 2 decimal places.
        :type latitude: float
        :param longitude: The longitude rounded to 2 decimal places.
        :type longitude: float
        """

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "us_aqi",
            "timezone": "auto",
            "forecast_days": 1,
        }
        data = self.api_call("air_quality", params=params)
        return int(data["current"]["us_aqi"])

    def get_api_speed_unit(self, unit: str) -> str:
        """
        Convert any speed unit into the API representation for the API Call.
        If an invalid unit is requested, it will raise an APIError.
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
        elif unit == "knots":
            return "kn"
        else:
            raise APIError(f"The configured unit {unit!r} wasn't matched with any supported unit.")

    def get_api_temperature_unit(self, unit: str) -> str:
        """
        Convert any temperature unit into the API representation for the API Call.
        The API can't handle kelvin, which means it has to be converted afterward. For easy conversion, Celsius will be used for the API call.
        If an invalid unit is requested, it will raise an APIError.
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
            raise APIError(f"The configured unit {unit!r} wasn't matched with any supported unit.")

    def get_api_precipitation_unit(self, unit: str) -> str:
        """
        Convert any precipitation unit into the API representation for the API Call.
        If an invalid unit is requested, it will raise an APIError.
        Default: "mm" (Millimeters)
        :param unit: This is the precipitation unit to get the API representation for.
        :type unit: str
        :return: API representation of the requested unit
        """
        if unit == "mm" or unit == "inch":
            return unit
        else:
            raise APIError(f"The configured unit {unit!r} wasn't matched with any supported unit.")
