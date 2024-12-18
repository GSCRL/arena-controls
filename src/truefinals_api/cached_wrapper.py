from time import time

from piccolo.engine.sqlite import SQLiteEngine

from config import settings as arena_settings
from truefinals_api.cached_api import (
    TrueFinalsTournamentsPlayers,
    getAllGames,
    getAllPlayersInTournament,
    getEventLocations,
)

lru_DB = SQLiteEngine(path="tf_lru.sqlite")

"""
Tournament locations call will return a list if there's more than one location / any is defined.

Location will return [] if there are no locations specified.

"""


def getAllTournamentsLocations():
    output_structure = []

    for tournament_key in arena_settings["tournament_keys"]:
        _current_fk = tournament_key["id"]
        _current_name = tournament_key["weightclass"]

        _current_data = getEventLocations(_current_fk)

        for loc in _current_data[0]["response"]:
            loc["root_tournament_fk"] = _current_fk
            loc["staleness_time"] = _current_data[0]["last_requested"]

            output_structure.append(loc)

    return output_structure


def getAllTournamentsPlayers():
    output_structure = []

    for tournament_key in arena_settings["tournament_keys"]:
        _current_fk = tournament_key["id"]
        _current_name = tournament_key["weightclass"]

        _current_data = getAllPlayersInTournament(_current_fk)

        for loc in _current_data[0]["response"]:
            # print(loc)
            loc["root_tournament_fk"] = _current_fk
            loc["staleness_time"] = _current_data[0]["last_requested"]

            output_structure.append(loc)

    # Reset this so we can re-analyze stuff and sanely interact with the data backed by the cache.
    # for item in output_structure:
    #

    return output_structure


def build_dict_from_db():
    matches_dict = {}

    if (
        len(
            TrueFinalsTournamentsPlayers.select()
            .where(TrueFinalsTournamentsPlayers.last_updated + 3600 > time())
            .output(load_json=True)
            .run_sync()
        )
        == 0
    ):
        TrueFinalsTournamentsPlayers.delete(force=True)

        all_tournaments_players = getAllTournamentsPlayers()

        # pprint(all_tournaments_players[0])

        refactor_list = [
            {
                "tournament_id": player_moment["root_tournament_fk"],
                "last_updated": time(),
                "player_data": player_moment,
            }
            for player_moment in all_tournaments_players
        ]

        for i in refactor_list:
            TrueFinalsTournamentsPlayers.insert(
                TrueFinalsTournamentsPlayers(
                    id=i["player_data"]["id"],
                    tournament_id=i["tournament_id"],
                    last_updated=i["last_updated"],
                    player_data=i["player_data"],
                )
            ).run_sync()

    for tournament_player in (
        TrueFinalsTournamentsPlayers.select().output(load_json=True).run_sync()
    ):
        if tournament_player["tournament_id"] not in matches_dict:
            matches_dict[tournament_player["tournament_id"]] = {}

        if (
            tournament_player["id"]
            not in matches_dict[tournament_player["tournament_id"]]
        ):
            matches_dict[tournament_player["tournament_id"]][
                tournament_player["id"]
            ] = tournament_player

    return matches_dict


def getPlayerByIds(tournamentID: str, playerID: str):
    value = build_dict_from_db()

    if tournamentID in value:
        if playerID in value[tournamentID]:
            return value[tournamentID][playerID]["player_data"]
    # fmt: off
    # This reflects all of the needed keys so we're kept sane-ish.  Yay.
    return {"id": None, "name": "Default Player Information",
            "photoUrl": None,
            "seed": -1,
            "wins": -1,
            "losses": -1,
            "ties": -1,
            "isBye": False,
            "isDisqualified": False,
            "lastPlayTime": 1734297074657,
            "lastBracketGameID": None,
            "placement": 99999999999,
            "profileInfo": None,
            "root_tournament_fk": "",
            "staleness_time": 9999999999999,
        }
    # fmt: on


def getAllTournamentsMatches():
    output_structure = []

    for tournament_key in arena_settings["tournament_keys"]:
        _current_fk = tournament_key["id"]
        _current_name = tournament_key["weightclass"]

        _current_data = getAllGames(_current_fk)

        # print(_current_data)

        if len(_current_data) == 1:
            print(
                f"Exactly one valid response in API cache for this invocation of get all games for tourney_fk of {_current_fk}."
            )

            for match in list(_current_data[0]["response"]):
                match["tournamentID"] = _current_fk
                match["weightclass"] = _current_name
                match["staleness_time"] = _current_data[0]["last_requested"]

                output_structure.append(match)

    return output_structure
