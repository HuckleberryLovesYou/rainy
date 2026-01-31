# Lazy loading modules

def main(args):
    import cli
    cli_options = cli.validate_args(args)

    import config
    config_obj = config.Config()

    if cli_options.reinitialize_config:
        config_obj.reinit_cfg_folder()

    config_settings = config_obj.get_config()
    city_name = None
    country_code = None

    if cli_options.city_name:
        city_name = cli_options.city_name

    if cli_options.country_code:
        country_code = cli_options.country_code

    if cli_options.history_index:

        import history
        history_obj = history.History()
        if cli_options.history_index == -1:
            history_obj.print_history()
            city_name = history_obj.load_city_at_index(int(input("Enter Index of history entry: ")))
        else:
            history_index: int = cli_options.history_index
            city_name = history_obj.load_city_at_index(history_index)
    else:
        history_obj = None

    import api
    api_obj = api.API()

    if not city_name:
        latitude, longitude, city_name = api_obj.get_location_by_ip()

    data = None
    if not cli_options.bypass_cache:
        import cache
        cache_obj = cache.Cache(config_obj)
        data = cache_obj.load_cache(city_name)
    else:
        cache_obj = None

    if not data:
        latitude, longitude, city_name = api_obj.get_location_by_city_name(city_name, country_code)

        api_speed_unit = api_obj.get_api_speed_unit(config_settings.speed_unit)
        api_temperature_unit = api_obj.get_api_temperature_unit(config_settings.temperature_unit)
        api_precipitation_unit = api_obj.get_api_precipitation_unit(config_settings.precipitation_unit)
        data = api_obj.get_weather_forecast(latitude, longitude, api_speed_unit, api_temperature_unit, api_precipitation_unit)

        if config_settings.show_air_quality:
            air_quality_index = api_obj.get_air_quality(latitude, longitude)
            data["current"].update({"us_aqi": air_quality_index})
        if not config_settings.max_cache_file_count == 0:
            if cache_obj is None:
                import cache
                cache_obj = cache.Cache(config_obj)
            cache_obj.write_cache(city_name, data)

    if history_obj is None:
        import history
        history_obj = history.History()
    history_obj.add_history(city_name)

    import weather
    import output
    weather_obj = weather.WeatherService()
    parsed_weather = weather_obj.parse_weather(city_name, data, config_settings)
    output.output(parsed_weather, config_settings)
