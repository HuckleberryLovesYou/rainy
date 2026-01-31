from models import Weather, ConfigSettings
import formatters

def output(weather: Weather, config: ConfigSettings) -> None:
    """
    Prints the output of rainy to the terminal. It can take any amount of parameters. If no parameter is passed, the output will only be the ascii art of the current weather.
    If the amount of lines needed to display the passed parameters, it will expand the ascii art with blank lines in the same amount of characters and add the value behind it.

    It will not return anything in any case.

    :return: None
    """
    local_date_time = formatters.get_local_date_time(weather.utc_offset_seconds, weather.sunrise_local, weather.sunset_local, config.date_format, config.time_format)

    values: dict[str, str | float] = {}
    if config.show_city:
        values["City"] = weather.city_name
    if config.show_weather:
        values["Weather"] = formatters.get_weather_name(weather.weather_code)
    if config.show_temperature:
        values["Temperature"] = formatters.get_temperature(weather.temperature, weather.apparent_temperature, weather.temperature_max, weather.temperature_min, config.temperature_unit, config.show_apparent_temperature, config.show_max_and_min_temperature)
    if config.show_wind_speed:
        values["Wind Speed"] = formatters.get_wind_speed(weather.wind_speed, config.speed_unit)
    if config.show_wind_direction:
        values["Wind Direction"] = formatters.get_wind_direction(weather.wind_direction)
    if config.show_sunrise:
        values["Sunrise"] = local_date_time.local_sunrise
    if config.show_sunset:
        values["Sunset"] = local_date_time.local_sunset
    if config.show_date:
        values["Date"] = local_date_time.local_date
    if config.show_time:
        values["Time"] = local_date_time.local_time
    if config.show_uv_index:
        values["UV Index"] = weather.uv_index
    if config.show_humidity:
        values["Humidity"] = formatters.get_humidity(weather.humidity_percent)
    if config.show_precipitation:
        values["Precipitation"] = formatters.get_precipitation(weather.precipitation, config.precipitation_unit)
    if config.show_surface_pressure:
        values["Surface Pressure"] = formatters.get_surface_pressure(weather.surface_pressure_hpa)
    if config.show_air_quality:
        values["Air Quality Index"] = formatters.get_air_quality_index_concern(weather.air_quality_index)

    use_emoji = config.use_emoji
    if config.show_ascii_art:
        ascii_art = formatters.get_ascii_art(weather.weather_code, weather.is_day)
        len_diff = len(values) - len(ascii_art)
        if len_diff > 0:

            blank_line = " " * 17
            ascii_art.extend([blank_line] * len_diff)

        bullet = " " if use_emoji else "○ "

        for i, (key, value) in enumerate(values.items()):
            try:
                if use_emoji:
                    output_line = ascii_art[i] + formatters.get_emoji(key) + " " + key + ": " + str(value)
                else:
                    output_line = ascii_art[i] + bullet + key + ": " + str(value)
                print(output_line)
            except IndexError:
                print(ascii_art[i])
    else:


        for key, value in values.items():
            if use_emoji:
                output_line = formatters.get_emoji(key) + " " + key + ": " + str(value)
            else:
                output_line = "○ " + key + ": " + str(value)
            print(output_line)