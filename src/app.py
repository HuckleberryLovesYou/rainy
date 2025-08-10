import cli
import config
import history
import api
import cache
import weather
import output

config = config.Config()
history = history.History()
api = api.API()
cache = cache.Cache(config)
weather = weather.WeatherService()

def main(args):
    cli_options = cli.validate_args(args)

    if cli_options.reinitialize_config:
        config.reinit_cfg_folder()

    config_settings = config.load_config()
    city_name = None
    country_code = None

    if cli_options.city_name:
        city_name = cli_options.city_name

    if cli_options.country_code:
        country_code = cli_options.country_code

    if cli_options.history_index:
        if cli_options.history_index == -1:
            history.print_history()
            city_name = history.load_city_at_index(int(input("Enter Index of history entry: ")))
        else:
            history_index: int = cli_options.history_index
            city_name = history.load_city_at_index(history_index)

    if not city_name:
        latitude, longitude, city_name = api.get_location_by_ip()

    data = None
    if not cli_options.bypass_cache:
        data = cache.load_cache(city_name)

    if not data:
        latitude, longitude, city_name = api.get_location_by_city_name(city_name, country_code)

        api_speed_unit = api.get_api_speed_unit(config_settings.speed_unit)
        api_temperature_unit = api.get_api_temperature_unit(config_settings.temperature_unit)
        api_precipitation_unit = api.get_api_precipitation_unit(config_settings.precipitation_unit)
        data = api.get_weather_forecast(latitude, longitude, api_speed_unit, api_temperature_unit, api_precipitation_unit)

        if config_settings.show_air_quality:
            air_quality_index = api.get_air_quality(latitude, longitude)
            data["current"].update({"us_aqi": air_quality_index})
        cache.write_cache(city_name, data)
    history.add_history(city_name)
    parsed_weather = weather.parse_weather(city_name, data, config_settings)
    output.output(parsed_weather, config_settings)
