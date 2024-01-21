import logging
import time

import httpx

from config import settings as arena_settings
from pprint import pprint

class APICache:
    def __init__(self, ttl=30):
        self._data = {}
        self.ttl = ttl

    def set(self, key, value):
        self._data[key] = {"requestTime": time.time(), "value": value}
        logging.info(
            f"key {key} now in cache with timestamp {self._data[key]['requestTime']} and value {value}"
        )
        return self._data[key]["value"]

    def get(self, key):
        if key in self._data:
            logging.info(f"key {key} present in cache")
            if "requestTime" in self._data[key]:
                logging.info(
                    f"time {self._data[key]['requestTime']} is present for value"
                )
                if (self._data[key]["requestTime"] + self.ttl) < time.time():
                    logging.info("value is not expired.")
                    #print(self._data[key]['value'])
                    return self._data[key]['value']

        return None


cache = APICache(ttl=60)


def makeAPIRequest(endpoint: str) -> list:
    api_key = arena_settings.truefinals.api_key
    user_id = arena_settings.truefinals.user_id
    credentials = {"user_id": user_id, "api_key": api_key}

    headers = {
        "x-api-user-id": credentials["user_id"],
        "x-api-key": credentials["api_key"],
    }

    root_endpoint = """https://truefinals.com/api"""

    pprint([{'requestTime':x['requestTime'], 'key':x['key']} for x in cache._data])

    if cache.get(endpoint) is None:
        print("value is not in cache, trying now!")
        resp = httpx.get((f"{root_endpoint}{endpoint}"), headers=headers)

        if resp.status_code == 429:
            logging.warning(f"Rate limit exceeded when calling endpoint {resp.url}")
        else:
            return cache.set(endpoint, resp.json())
        logging.info({resp, resp.url, resp.status_code})

    else:
        print("value is in cache, yay!")
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
