import os
import json
import time # TODO: Get rid of time dependency
import config

cache_file_name: str = r"cache.json"


class Cache:
    def __init__(self):
        self.abs_cache_folder_path: str = config.Config().get_abs_cache_folder_path()
        self.cache_ttl: int = 360
        self.max_cache_file_count: int = 10


    def get_abs_cache_file_path(self, city) -> str:
        return os.path.join(self.abs_cache_folder_path, f"cache_{city.replace(" ", "-")}.json")


    def count_cache_files(self) -> int:
        return len(os.listdir(self.abs_cache_folder_path))


    def get_oldest_cache_file_path(self) -> str:
        data = []
        for cache_file in os.listdir(self.abs_cache_folder_path):
            cache_file_path = os.path.join(self.abs_cache_folder_path, cache_file)
            modification_time = os.path.getmtime(cache_file_path)
            data.append([cache_file_path, modification_time])

        data.sort(key=lambda sublist: sublist[1])
        return data[0][0]


    def write_cache(self, city: str, cache: str):
        while self.count_cache_files() >= self.max_cache_file_count:  # While loop needed to adapt if config max_cache_file_count changed blow the current cache file count
            os.remove(self.get_oldest_cache_file_path())  # Removes the oldest cache if max cache count is reached

        with open(self.get_abs_cache_file_path(city), "w") as file:
            file.write(cache)


    def load_cache(self, city: str) -> dict | None:
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