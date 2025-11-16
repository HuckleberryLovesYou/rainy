import argparse
from models import CliOptions
from exceptions import CliArgsError

version = r"1.3.0"

def parse_cli_args():
    parser = argparse.ArgumentParser(
        prog="Rainy",
        description="Neofetch-like, minimalistic, and customizable weather-fetching tool. Anything set using CLI-Arguments is only used for one execution of rainy. To make persistent changes edit the configuration file.",
        epilog="Example: %(prog)s --city-name Potsdam --country-code DE"
    )
    parser.add_argument("-c", "--city-name", dest="city_name", help="Specify the city name to look for. For example for Potsdam the cit name would be 'Potsdam'. If not specified, looks up location by your public IP.", type=str)
    parser.add_argument("-country", "--country-code", dest="country_code", help="Specify the country code for the country to look for the specified city . A List of Country Codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements", type=str)
    parser.add_argument("--reinit", dest="reinitialize_config", action="store_true", help="This re-initializes the configuration folder at ~/.rainy. This will also delete cache and configuration.")
    parser.add_argument("--bypass-cache", dest="bypass_cache", action="store_true", help="This allows you to bypass the cache stored at ~/.rainy/cache.")
    parser.add_argument("-v", "--version", dest="show_version", action="store_true", help="This shows the version of rainy.")
    parser.add_argument("--history", nargs="?", const=-1, default=None, type=int, help="If given with no number (e.g. `--history`), history will be –1; if you pass a number (e.g. `--history 3`), you get that index. If you omit the flag entirely, history is None.")

    try:
        return parser.parse_args()
    except SystemExit:
        # Help was triggered or parsing failed
        exit()

def validate_args(args):
    options = CliOptions(
        city_name=args.city_name,
        country_code=args.country_code,
        history_index=args.history,
        bypass_cache=args.bypass_cache,
        reinitialize_config=args.reinitialize_config,
        show_version=args.show_version,
        verbose=False,
        quiet=False,
        refresh=False,
        temperature_unit_override=None,
        speed_unit_override=None,
        precipitation_unit_override=None,
        date_format_override=None,
        time_format_override=None,
    )

    if options.country_code and not options.city_name:
        raise CliArgsError("--country-code was specified but --city-name wasn't. --country-code requires --city-name")

    if options.show_version:
        print(f"You are running version {version!r} of rainy by HuckleberryLovesYou.")
        exit()

    return options