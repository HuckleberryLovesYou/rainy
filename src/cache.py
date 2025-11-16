import os
import json
import time
from typing import Any
from models import ConfigSettings

cache_file_name: str = r"cache.json"


class Cache:
    def __init__(self, config):
        self.abs_cache_folder_path: str = config.abs_cache_folder_path

        config_settings: ConfigSettings = config.get_config()
        self.cache_ttl: int = config_settings.cache_ttl
        self.max_cache_file_count: int = config_settings.max_cache_file_count


    def get_abs_cache_file_path(self, city) -> str:
        """
        This gets the absolute file path of the cache file. The name of the file itself consists of the letters 'cache_', followed by the name of the city where spaces are replaced with dashes and followed by .json.
        :param city:
        :return: Returns the absolute file path of the cache file.
        """
        return os.path.join(self.abs_cache_folder_path, f"cache_{city.replace(' ', '-')}.json")


    def count_cache_files(self) -> int:
        return len(os.listdir(self.abs_cache_folder_path))


    def get_oldest_cache_file_path(self) -> str:
        """
        This function gets the absolute file path of the oldest cache determined by the modification time.
        :return:
        """
        cache_files: list[str] = []
        for cache_file in os.listdir(self.abs_cache_folder_path):
            abs_cache_file_path = os.path.join(self.abs_cache_folder_path, cache_file)
            if os.path.isfile(abs_cache_file_path):
                cache_files.append(abs_cache_file_path)

        return min(cache_files, key=os.path.getmtime)


    def write_cache(self, city: str, data: Any):
        while self.count_cache_files() >= self.max_cache_file_count:  # While loop needed to adapt if config max_cache_file_count changed blow the current cache file count
            os.remove(self.get_oldest_cache_file_path())  # Removes the oldest cache if max cache count is reached

        with open(self.get_abs_cache_file_path(city), "w") as file:
            file.write(json.dumps(data))


    def load_cache(self, city: str) -> dict | None:
        print("Looking for cache...", end="\r")
        if self.is_cache_present(city) and self.is_cache_valid(city):
            with open(self.get_abs_cache_file_path(city), "r") as file:
                return json.load(file)
        return None


    def is_cache_present(self, city):
        abs_cache_file_path = self.get_abs_cache_file_path(city)
        if not os.path.exists(abs_cache_file_path):
            print(f"Cache is empty.", end="\r")
            return False
        if os.path.getsize(abs_cache_file_path) <= 0:
            print("Cache file is empty.", end="\r")
            return False
        return True


    def is_cache_valid(self, city):
        if (round(time.time()) - round(os.path.getmtime(self.get_abs_cache_file_path(city)))) <= self.cache_ttl:
            return True
        print("Cache has expired...", end="\r")
        return False