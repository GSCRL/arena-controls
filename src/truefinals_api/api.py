import json
import logging
import time
from copy import deepcopy

import httpx

from config import settings as arena_settings, secrets as arena_secrets

# This was shamelessly copied and may not work
# as intended.  The intent is to move the API
# request workers to the background such that
# they can be polled on more regular intervals
# stored in memory, and then periodically giv-
# en to clients for the most up-to-date match
# behavior without needing to potentially hit
# an error state.


class APICache:
    def __init__(self, ttl=30):  # 30s cache, hopefully good.
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

from httpx import Client

tf_api_session = Client()
# This caches the items less likely to change (if at all during the
# course of the event.  The field software probably shouldn't be
# called until this is set up finally and tournaments are started.


def makeAPIRequest(endpoint: str) -> list:
    api_key = arena_secrets.truefinals.api_key
    user_id = arena_secrets.truefinals.user_id
    credentials = {"user_id": user_id, "api_key": api_key}

    headers = {
        "x-api-user-id": credentials["user_id"],
        "x-api-key": credentials["api_key"],
    }

    root_endpoint = """https://truefinals.com/api"""

    logging.info(f"value {endpoint} is not in cache, trying request now!")
    resp = tf_api_session.get((f"{root_endpoint}{endpoint}"), headers=headers)
    return resp


def getAllTourneys(credentials) -> list[dict]:
    x = makeAPIRequest("/v1/user/tournaments", credentials)
    return x


def getEventInformation(tournamentID: str) -> dict:
    return makeAPIRequest(f"/v1/tournaments/{tournamentID}")


def getAllGames(tournamentID: str) -> list[dict]:
    return makeAPIRequest(f"/v1/tournaments/{tournamentID}/games")


def getAllPlayersInTournament(tournamentID: str) -> list[dict]:
    return makeAPIRequest(f"/v1/tournaments/{tournamentID}/players")
