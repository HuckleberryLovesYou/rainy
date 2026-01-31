from models import Weather, ConfigSettings, TemperatureUnit, Coordinates

class WeatherService:
    def parse_weather(self, city_name: str, data: dict, config_settings: ConfigSettings) -> Weather:
        """

        :param city_name: The name of the city the data was fetched for
        :param data: The data fetched by the forecast API and if needed by the Air Quality API
        :param config_settings: The Settings fetched from the Configuration
        :return: tuple: It contains the weather_code (a WMO Weather interpretation (WW) code that describes the current weather (1-99) (https://open-meteo.com/en/docs))
        """

        current = data["current"]
        daily = data["daily"]

        air_quality_index = current.get("us_aqi") if config_settings.show_air_quality else None

        temperature = current["temperature_2m"]
        apparent_temperature = current["apparent_temperature"]
        temperature_max = daily["temperature_2m_max"][0]
        temperature_min = daily["temperature_2m_min"][0]

        # Only convert for Kelvin (avoid checking string repeatedly)
        if config_settings.temperature_unit == TemperatureUnit.KELVIN.value:
            kelvin_offset = 273.2
            temperature += kelvin_offset
            apparent_temperature += kelvin_offset
            temperature_max += kelvin_offset
            temperature_min += kelvin_offset

        sunrise_local = daily["sunrise"][0][-5:]
        sunset_local = daily["sunset"][0][-5:]

        weather = Weather(
            city_name=city_name,
            coordinates=Coordinates(
                latitude=data["latitude"],
                longitude=data["longitude"],
            ),
            utc_offset_seconds=data["utc_offset_seconds"],
            weather_code=current["weather_code"],
            sunrise_local=sunrise_local,
            sunset_local=sunset_local,
            temperature=temperature,
            temperature_max=temperature_max,
            temperature_min=temperature_min,
            apparent_temperature=apparent_temperature,
            uv_index=daily["uv_index_max"][0],
            wind_speed=current["wind_speed_10m"],
            wind_direction=current["wind_direction_10m"],
            is_day=current["is_day"],
            humidity_percent=current["relative_humidity_2m"],
            precipitation=current["precipitation"],
            surface_pressure_hpa=current["surface_pressure"],
            air_quality_index=air_quality_index
        )

        return weather
