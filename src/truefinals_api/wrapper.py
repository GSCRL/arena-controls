import json
import logging
import time
from pathlib import Path
from pprint import pprint
from typing import Self

from config import settings as arena_settings
from truefinals_api.api import getAllGames, getAllPlayersInTournament, getAllTourneys

"""Helper function to check whether the player is a legitimate player or to get a bye.

Terrible and only used for when the filtering to remove byes doesn't work."""


class Matches:
    def __init__(self, eventID=None, matches=None):
        self._eventID = eventID
        self._matches = matches

        if self._matches is None and self._eventID != None:
            self._matches = getAllGames(self._eventID)

    def __repr__(self):
        return {"tournamentID": self._eventID, "matches": self._matches}

    # Todo, accept arbitrary lambda so this greatly simplifies our user-side code I guess?  idk.
    def withFilter(self, filterFunction):
        pass

    def withoutByes(self):
        _matches = self._matches
        for m in _matches:
            m["slots"] = [c for c in m["slots"] if not c["playerID"].startswith("bye")]

        return Matches(self._eventID, matches=_matches)

    def toFile(self, path: str):
        with open(Path(path), "w") as output:
            output.write(json.dumps(self._matches, indent=4))


class Match:
    def __init__(self, match_item: dict):
        self.match_json_original = match_item
        self.players = self.match_json_original["slots"]

    # Todo, test.
    def numPlayers(self, includeByes=False):
        if includeByes:  # Should include all competitors in a given match.
            return len(self.players)
        return len([x for x in self.players if x["playerID"] is None])

    def matchState(self):
        return self.match_json_original["state"]

    def backfillPlayerWLT(self, allCompetitors: list):
        def _playerIDToName(allCompetitors: list, playerID: str):
            for c in allCompetitors:
                if c["id"] is playerID:
                    return c
            if playerID.startswith("bye"):
                return self._generateBye()
            logging.warning(
                f"did not find competitor, oops!  Was looking for {playerID}"
            )

        def _generateBye(self):
            return {
                "name": "Bye",
                "seed": -1,
                "wins": -1,
                "losses": -1,
                "ties": -1,
                "bye": True,
            }


class TrueFinals:
    def __init__(self):
        if "truefinals" in arena_settings:
            api_key = arena_settings.truefinals.api_key
            user_id = arena_settings.truefinals.user_id
            self._credentials = {"user_id": user_id, "api_key": api_key}

    def getAllPlayersOfTournament(self, tournamentID: str) -> list[dict]:
        players = getAllPlayersInTournament(self._credentials, tournamentID)
        return players

    def getAllMatches(self, tournamentID: str) -> Matches:
        matches = Matches(eventID=tournamentID)
        return matches

    def getFinishedMatches(self, tournamentID: str) -> list[dict]:
        pass

    def getUnfinishedMatches(self, tournamentID: str) -> list[dict]:
        pass

    def getMatchesInOrder(self, cross_div_matches: list):
        pass

    def getAllFinishedCrossDivMatches(self, divisions):
        pass

    def getAllUnfinishedCrossDivMatches(self, divisions):
        pass
