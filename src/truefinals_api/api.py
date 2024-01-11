import httpx
import logging

# Very much a WIP.  While we _can_ use OpenAPI to generate all of the API interfaces automagically, it'll likely only implement the functions needed below.


def makeAPIRequest(endpoint: str, credentials: dict) -> list:
    if len(credentials) != 2:
        raise Exception(
            """Credentials not in format of {"user_id": "","api_key":""}.  See TrueFinals API docs for more info."""
        )

    headers = {
        "x-api-user-id": credentials["user_id"],
        "x-api-key": credentials["api_key"],
    }

    root_endpoint = """https://truefinals.com/api"""

    resp = httpx.get((f"{root_endpoint}{endpoint}"), headers=headers)

    logging.info({resp, resp.url})
    return resp.json()


def getAllTourneys(credentials) -> list[dict]:
    x = makeAPIRequest("/v1/user/tournaments", credentials)


def getAllGames(credentials, tournamentID: str) -> list[dict]:
    x = makeAPIRequest(f"/v1/tournaments/{tournamentID}/games", credentials)
    return x


# This enumerates all matches with one or more players labeled to show in the "upcoming matches" bracket.  Still need to figure out the filtering stuff.
def getAllGamesWithOneOrMoreCompetitors(credentials, tournamentID: str) -> list[dict]:
    allGames = getAllGames(credentials, tournamentID)

    def howManyPlayersAreFilledIn(games: list) -> list:
        game_out = []
        for game in games:
            if "slots" in game:
                total = 0
                for player in game["slots"]:
                    if player["playerID"] != None:
                        total += 1

                if total != 0:
                    game_out.append(game)

        return game_out

    filteredGames = howManyPlayersAreFilledIn(allGames)

    return filteredGames


def getAllPlayersInTournament(credentials, tournamentID: str) -> list[dict]:
    players = makeAPIRequest(f"/v1/tournaments/{tournamentID}/players", credentials)

    return players
