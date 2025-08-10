from models import Weather, ConfigSettings, TemperatureUnit, Coordinates

class WeatherService:
    def parse_weather(self, city_name: str, data: dict, config_settings: ConfigSettings) -> Weather:
        """

        :param city_name: The name of the city the data was fetched for
        :param data: The data fetched by the forecast API and if needed by the Air Quality API
        :param config_settings: The Settings fetched from the Configuration
        :return: tuple: It contains the weather_code (a WMO Weather interpretation (WW) code that describes the current weather (1-99) (https://open-meteo.com/en/docs))
        """
        air_quality_index = None
        if config_settings.show_air_quality:
            air_quality_index = int(data["current"]["us_aqi"])

        temperature = float(data["current"]["temperature_2m"])
        apparent_temperature = float(data["current"]["apparent_temperature"])
        temperature_max = float(data["daily"]["temperature_2m_max"][0])
        temperature_min = float(data["daily"]["temperature_2m_min"][0])

        if config_settings.temperature_unit == TemperatureUnit.KELVIN.value:
            temperature += 273.2
            apparent_temperature += 273.2
            temperature_max += 273.2
            temperature_min += 273.2


        weather = Weather(
            city_name=city_name,
            coordinates=Coordinates(
                latitude=round(float(data["latitude"]), 2),
                longitude=round(float(data["longitude"]), 2),
            ),
            utc_offset_seconds=int(data["utc_offset_seconds"]),
            weather_code=int(data["current"]["weather_code"]),
            sunrise_local="".join(data["daily"]["sunrise"])[-5:],
            sunset_local="".join(data["daily"]["sunset"])[-5:],
            temperature=temperature,
            temperature_max=temperature_max,
            temperature_min=temperature_min,
            apparent_temperature=apparent_temperature,
            uv_index=float(data["daily"]["uv_index_max"][0]),
            wind_speed=float(data["current"]["wind_speed_10m"]),
            wind_direction=int(data["current"]["wind_direction_10m"]),
            is_day=bool(data["current"]["is_day"]),
            humidity_percent=int(data["current"]["relative_humidity_2m"]),
            precipitation=float(data["current"]["precipitation"]),
            surface_pressure_hpa=float(data["current"]["surface_pressure"]),
            air_quality_index=air_quality_index
        )

        return weather
