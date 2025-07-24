import configparser
import time
import os
import json

cfg_folder_name: str = r".rainy"
cfg_file_name: str = r"config.ini"
cache_file_name: str = r"cache.json"
cache_ttl: int = 360

class Config:
    def __init__(self):
        self.abs_home_path: str = str(os.path.expanduser("~"))
        self.abs_cfg_folder_path: str = os.path.join(self.abs_home_path, cfg_folder_name)
        self.abs_cache_file_path: str = os.path.join(self.abs_cfg_folder_path, cache_file_name)
        self.abs_cfg_file_path: str = os.path.join(self.abs_cfg_folder_path, cfg_file_name)

        if not os.path.exists(self.abs_cfg_folder_path):
            self.create_cfg_folder()


    def create_cfg_folder(self, reinit: bool = False):
        if reinit:
            self.remove_directory_tree(self.abs_cfg_folder_path)

        if os.path.exists(self.abs_cfg_folder_path):
            print(f"Configuration Folder already exists at '{self.abs_cfg_folder_path}'. Skipping creation. If this is wrong you can recreate this folder by passing --reinit to rainy.py.")
            return None

        os.mkdir(self.abs_cfg_folder_path)
        print(f"Created .rainy folder at {self.abs_cfg_folder_path}.")
        with open(self.abs_cfg_file_path, "w") as file:
            file.write("""# Configuration File for rainy.
# Any values can be changed using CLI-Arguments as well.

# Any Location settings are optional. If Values are unset rainy will get your location based on your public IP. The public IP will not be shown.
[Location]
# Specify the city name to lookup the weather for.
city_name:

# Specify the country code of the country to look for the above specified city name. For example for Germany the country code would be 'DE'. A list of all country codes can be found here: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements
country_code:

[Units]
# Specify the unit of measurement for the temperature. Following units are valid: C, F, K
temperature_unit: C

# Specify the unit of measurement for the speed of the wind. Following units are valid: mph, km/h, m/s, Knots
speed_unit = km/h

# Specify the unit of measurement for the speed of the wind. Following units are valid: mm, inch
precipitation_unit = mm

[Formats]
# Specify the date format. Following formats are valid: MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, YYYY-MM-DD, DD.MM.YYYY
date_format = DD.MM.YYYY

# Specify the time format. Following formats are valid: 12, 24
time_format = 24

[Show]
# Show the city name, True or False
show_city = True

# Shows the word-representation of the weather shown in the ascii art, True or False
show_weather = True

# Show the temperature, True or False
show_temperature = True

# Show the apparent (feels like) temperature, True or False
show_apparent_temperature = False

# Show the daily maximum and minimum temperature, True or False
show_max_and_min_temperature = True

# Show the wind speed, True or False
show_wind_speed = True

# Show the wind direction, True or False
show_wind_direction = True

# Show the sunrise, True or False
show_sunrise = True

# Show the sunset, True or False
show_sunset = True

# Shows the current date. True or False
show_date = True

# Shows the current time. True or False
show_time = True

# Shows the current UV index. True or False
show_uv_index = True

# Shows the current humidity. True or False
show_humidity = True

# Shows the precipitation within the next hour. True or False
show_precipitation = True

# Shows the current surface pressure in hPa. True or False
show_surface_pressure = True


[Output]
# Specify if the output should contain emojis to the corresponding output line, True or False
use_emoji = False

# Specify if the output should be colored to the corresponding output line, True or False
use_color = False

# Specify if the output should contain the ASCII-Art of the corresponding weather, True or False
show_ascii_art = True""")
        print(f"Created configuration file at '{self.abs_cfg_file_path}'.")
        return None

    def remove_directory_tree(self, start_directory: str):
        """
        Recursively and permanently removes the specified directory, all of its
        subdirectories, and every file contained in any of those folders.
        """
        for name in os.listdir(start_directory):
            path = os.path.join(start_directory, name)
            if os.path.isfile(path):
                os.remove(path)
            else:
                self.remove_directory_tree(path)
        os.rmdir(start_directory)

    def write_cache(self, city: str, cache: str):
        with open(self.abs_cache_file_path, "w") as file:
            file.write(f"{city}|{cache}")

    def load_cache(self, requested_city: str) -> dict | None:
        if self.is_cache_present() and self.is_cache_valid():
            with open(self.abs_cache_file_path, "r") as file:
                cache = file.read()
                found_city: str = cache.split("|")[0]
                if found_city == requested_city:
                    return json.loads(cache.split("|")[1])
        return None

    def is_cache_present(self):
        if not os.path.exists(self.abs_cache_file_path):
            print(f"Cache File not found at {self.abs_cache_file_path}")
            return False
        if os.path.getsize(self.abs_cache_file_path) <= 0:
            print("Cache is empty.")
            return False
        return True

    def is_cache_valid(self):
        if (round(time.time()) - round(os.path.getmtime(self.abs_cache_file_path))) <= cache_ttl:
            return True
        print("Cache is over TimeToLive.")
        return False


    def load_config(self):
        parser = configparser.ConfigParser()
        parser.read(self.abs_cfg_file_path)

        # load configuration
        cfg = {
            # Location
            "city_name": parser.get("Location", "city_name"),
            "country_code": parser.get("Location", "country_code"),

            # Units
            "temperature_unit": "°" + parser.get("Units", "temperature_unit"),
            "speed_unit": parser.get("Units", "speed_unit"),
            "precipitation_unit": parser.get("Units", "precipitation_unit"),

            # Formats
            "date_format": parser.get("Formats", "date_format"),
            "time_format": parser.getint("Formats", "time_format"),

            # What to show
            "show_city": parser.getboolean("Show", "show_city"),
            "show_weather": parser.getboolean("Show", "show_weather"),
            "show_temperature": parser.getboolean("Show", "show_temperature"),
            "show_apparent_temperature": parser.getboolean("Show", "show_apparent_temperature"),
            "show_max_and_min_temperature": parser.getboolean("Show", "show_max_and_min_temperature"),
            "show_wind_speed": parser.getboolean("Show", "show_wind_speed"),
            "show_wind_direction": parser.getboolean("Show", "show_wind_direction"),
            "show_sunrise": parser.getboolean("Show", "show_sunrise"),
            "show_sunset": parser.getboolean("Show", "show_sunset"),
            "show_date": parser.getboolean("Show", "show_date"),
            "show_time": parser.getboolean("Show", "show_time"),
            "show_uv_index": parser.getboolean("Show", "show_uv_index"),
            "show_humidity": parser.getboolean("Show", "show_humidity"),
            "show_precipitation": parser.getboolean("Show", "show_precipitation"),
            "show_surface_pressure": parser.getboolean("Show", "show_surface_pressure"),

            # Output options
            "use_emoji": parser.getboolean("Output", "use_emoji"),
            "use_color": parser.getboolean("Output", "use_color"),
            "show_ascii_art": parser.getboolean("Output", "show_ascii_art"),
        }
        return cfg