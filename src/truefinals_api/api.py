import json
import logging
import time
from copy import deepcopy

import httpx

from config import settings as arena_settings


class APICache:
    def __init__(self, ttl=30):
        self._data = {}
        self.ttl = ttl

    def set(self, key, value):
        self._data[key] = {"requestTime": time.time(), "value": deepcopy(value)}
        logging.info(
            f"key {key} now in cache with timestamp {self._data[key]['requestTime']} and value {json.dumps(value)[100:]}"
        )
        return self._data[key]["value"]

    def get(self, key):
        if key in self._data:
            logging.info(f"key {key} present in cache")
            if "requestTime" in self._data[key]:
                logging.info(
                    f"time {self._data[key]['requestTime']} is present for value"
                )
                logging.info(f"TTL is set to {self.ttl}")
                calculated_max_time = self._data[key]["requestTime"] + self.ttl
                logging.info(
                    f"Max expiry time is {calculated_max_time}, current time is {time.time()}"
                )
                if calculated_max_time < time.time():
                    logging.info("value is expired.")
                    return None
                else:
                    logging.info("Value not expired")
                    return self._data[key]["value"]

        return None


cache = APICache(ttl=120)


def makeAPIRequest(endpoint: str) -> list:
    api_key = arena_settings.truefinals.api_key
    user_id = arena_settings.truefinals.user_id
    credentials = {"user_id": user_id, "api_key": api_key}

    headers = {
        "x-api-user-id": credentials["user_id"],
        "x-api-key": credentials["api_key"],
    }

    root_endpoint = """https://truefinals.com/api"""

    if cache.get(endpoint) is None:
        logging.info(f"value {endpoint} is not in cache, trying request now!")
        resp = httpx.get((f"{root_endpoint}{endpoint}"), headers=headers)

        if resp.status_code == 429:
            logging.warning(f"Rate limit exceeded when calling endpoint {resp.url}")

        cache.set(endpoint, resp.json())
    return cache.get(endpoint)


def getAllTourneys(credentials) -> list[dict]:
    x = makeAPIRequest("/v1/user/tournaments", credentials)
    return x


def getAllGames(tournamentID: str) -> list[dict]:
    x = makeAPIRequest(f"/v1/tournaments/{tournamentID}/games")
    return x


def getAllPlayersInTournament(tournamentID: str) -> list[dict]:
    players = makeAPIRequest(f"/v1/tournaments/{tournamentID}/players")

    return players
