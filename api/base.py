import requests
import json
from time import sleep
from datetime import datetime, timezone
from typing import Tuple, Dict, AnyStr
from dotenv import dotenv_values
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = dotenv_values(".env")


def cooldown():
    def decorator(function):
        def wrapper(self: "BaseAPI", *args, **kwargs):
            response_code, response_data = function(self, *args, **kwargs)
            if response_code == 200 or not self.cooldown_expires:
                return response_code, response_data

            expires = datetime.strptime(
                self.cooldown_expires, "%Y-%m-%dT%H:%M:%S.%fZ"
            ).replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            sleep_duration = (expires - now).total_seconds()

            if sleep_duration > 0:
                sleep(sleep_duration)

            response_code, response_data = function(self, *args, **kwargs)
            return response_code, response_data

        return wrapper

    return decorator


class BaseAPI:
    def __init__(self) -> None:
        self.token = config["ARTIFACTS_TOKEN"]
        self.host = "https://api.artifactsmmo.com"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.token = self.token
        self.cooldown_expires = None

    @cooldown()
    def post(self, method: AnyStr, body: Dict = {}) -> Tuple[int, Dict]:
        url = self.host + method

        while True:
            try:
                response = requests.post(
                    url, headers=self.headers, data=json.dumps(body), verify=False
                )
                response_code = response.status_code
                if response_code == 429:
                    raise requests.exceptions.ConnectionError
                response_data = json.loads(response.text)
                break
            except (requests.exceptions.ConnectionError, json.JSONDecodeError):
                sleep(1)

        try:
            self.cooldown_expires = response_data["data"]["cooldown"]["expiration"]
        finally:
            return response_code, response_data

    @cooldown()
    def get(self, method: AnyStr, params: Dict = {}) -> Tuple[int, Dict]:
        url = self.host + method
        while True:
            try:
                response = requests.get(
                    url, headers=self.headers, params=params, verify=False
                )
                response_code = response.status_code
                if response_code == 429:
                    raise requests.exceptions.ConnectionError
                response_data = json.loads(response.text)
                break
            except (requests.exceptions.ConnectionError, json.JSONDecodeError):
                sleep(1)

        try:
            self.cooldown_expires = response_data["data"]["cooldown"]["expiration"]
        finally:
            return response_code, response_data

    def get_all(self, method: AnyStr, params: Dict = {}):
        params = {"page": 1, "size": 100}

        all_data = []

        _, response = self.get(method=method, params=params)

        total_pages = response["pages"]

        for i in range(1, total_pages + 1):
            params = {"page": i, "size": 100}
            _, response = self.get(method=method, params=params)
            all_data += response["data"]
            sleep(0.1)

        return all_data
