import os
import json

import config

config = config.Config()

history_file_name: str = r"history.txt"
max_history_count: int = 10

class History:
    def __init__(self):
        self.abs_history_folder_path = config.abs_history_folder_path
        self.abs_history_file_path = os.path.join(self.abs_history_folder_path, history_file_name)


    def add_history(self, city: str) -> None:
        if os.path.exists(self.abs_history_file_path):
            with open(self.abs_history_file_path, "r") as file:
                history: list[str] = json.loads(file.read())
        else:
            history = []


        if (len(history) + 1) >= max_history_count:
            history.pop(0)

        if city not in history:
            history.append(city)

        with open(self.abs_history_file_path, "w") as file:
            file.write(json.dumps(history))

    def load_history(self) -> list[str]:
        if not os.path.exists(self.abs_history_file_path):
            raise Exception("History File not existing. The history is only available if you already used rainy.")
        with open(self.abs_history_file_path, "r") as file:
            history = json.loads(file.read())
            history.reverse()
            return history

    def load_city_at_index(self, index: int):
        history = self.load_history()
        if 1 > index or index > len(history):
            raise Exception("Choose an index within the printed range.")

        return history[index - 1]

    def print_history(self) -> None:
        history = self.load_history()
        for index, city in enumerate(history):
            print(f"{int(index) + 1}: {city}")