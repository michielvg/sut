import json
from pathlib import Path

class Config:
    def __init__(self, config_file: str):
        self.data: dict = {}
        self.config_file = config_file
        self.load(config_file)

    def load(self, config_file: str):
        path = Path(config_file)

        if not path.is_file():
            print(f"Warning: config file '{config_file}' not found. Using defaults.")
            self.data = {}
            return

        try:
            with open(config_file) as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"Error: config file '{config_file}' must contain a JSON object.")
                self.data = {}
                return

            self.data = data

        except (json.JSONDecodeError, OSError) as e:
            print(f"Error: failed to load config file '{config_file}': {e}")
            self.data = {}

    def get_section(self, section: str) -> dict | bool | None:
        """
        Return the section dict, False, or None.
        - dict → normal section
        - None → section missing or null
        - False → section explicitly disabled
        """
        return self.data.get(section, None)