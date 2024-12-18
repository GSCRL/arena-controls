import logging
from time import time

from piccolo.columns import JSON, UUID, BigInt, Boolean, Text
from piccolo.engine.sqlite import SQLiteEngine
from piccolo.table import Table

from config import settings as arena_settings
from truefinals_api.cached_api import TrueFinalsAPICache
from truefinals_api.cached_api import (
    getAllGames,
    getAllPlayersInTournament,
    getEventInformation,
    getEventLocations,
)
from copy import copy

from pprint import pprint

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

        # output_structure.append(_current_data[0]["response"])

    return output_structure
