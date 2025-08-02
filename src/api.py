import requests

class API:
    def get_location_by_ip(self) -> tuple[float, float, str]:
        """
        Gets the current location of the user based on his public IP Address using the ipinfo.io API.
        If the User uses a VPN or Proxy, the location got, will be the location of the proxy or the VPN exit node.
        The latitude and longitude are rounded to 2 decimal places.

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

    def get_location_by_city_name(self, city_name: str, country_code: str | None = None) -> tuple[float, float, str]:
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

    def get_weather_by_api(self, latitude: float, longitude: float, wind_speed_unit: str, temperature_unit: str, precipitation_unit: str) -> dict:
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
        weather_api_response = requests.get(weather_api_uri, params=params)  # https://api.open-meteo.com/v1/forecast?latitude=37.335480&longitude=-121.893028&timezone=auto&forecast_days=1
        weather_api_response.raise_for_status()
        return weather_api_response.json()


    def get_air_quality_index_by_api(self, latitude: float, longitude: float) -> int:
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