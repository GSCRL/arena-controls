import json
import logging

import httpx

from config import settings as arena_settings

# Very much a WIP.  While we _can_ use OpenAPI to generate all of the API interfaces automagically, it'll likely only implement the functions needed below.


def makeAPIRequest(endpoint: str) -> list:
    if "truefinals" in arena_settings:
        api_key = arena_settings.truefinals.api_key
        user_id = arena_settings.truefinals.user_id
        credentials = {"user_id": user_id, "api_key": api_key}

    headers = {
        "x-api-user-id": credentials["user_id"],
        "x-api-key": credentials["api_key"],
    }

    root_endpoint = """https://truefinals.com/api"""

    resp = httpx.get((f"{root_endpoint}{endpoint}"), headers=headers)

    logging.info({resp, resp.url, resp.status_code})
    logging.info(json.dumps(resp.json(), indent=4))

    if resp.status_code == 429:
        logging.warning(f"Rate limit exceeded when calling endpoint {resp.url}")
    if resp.json() != None:
        return resp.json()
    else:
        return None


def getAllTourneys(credentials) -> list[dict]:
    x = makeAPIRequest("/v1/user/tournaments", credentials)
    return x


def getAllGames(tournamentID: str) -> list[dict]:
    x = makeAPIRequest(f"/v1/tournaments/{tournamentID}/games")
    return x


def getAllPlayersInTournament(tournamentID: str) -> list[dict]:
    players = makeAPIRequest(f"/v1/tournaments/{tournamentID}/players")

    return players
