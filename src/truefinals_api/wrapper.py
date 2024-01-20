import json
from copy import deepcopy
from pathlib import Path
from typing import Callable, Self

from config import settings as arena_settings
from truefinals_api.api import getAllGames, getAllPlayersInTournament

"""Helper function to check whether the player is a legitimate player or to get a bye.

Terrible and only used for when the filtering to remove byes doesn't work."""


class Matches:
    def __init__(
        self,
        eventID=None,
        matches: list = None,
        multiple_tournaments: bool = None,
        competitors: list = None,
        weightclass: str = None,
    ):
        self._eventID: str = eventID
        self._matches: list = matches
        self._competitors: list = competitors
        self._multiple_tournaments: bool = multiple_tournaments
        self._weightclass = weightclass

        if self._matches is None and self._eventID != None:
            self._matches = getAllGames(self._eventID)
            self._competitors = getAllPlayersInTournament(self._eventID)

        if self._eventID != None:
            for match in self._matches:
                # In the event the eventID is none, the tournamentID of a given match should be added to said construction.
                # If already present, skip it.  This allows merging of matches of multiple tournaments together fairly "easily".
                if "tournamentID" not in match:
                    match["tournamentID"] = self._eventID

                # Same logic to filter by weightclass in the output / render it.
                if 'weightclass' not in match:
                    match['weightclass'] = self._weightclass
                    

            self.backfillNames()

        # This captures if an erroneous list is merged / combined, having a single tournamentID does not apply anymore.
        if self._multiple_tournaments:
            self._eventID = None

    def __repr__(self):
        return {"tournamentID": self._eventID, "matches": self._matches}

    def backfillNames(self, competitors: list = None):
        _matches = deepcopy(self)
        if self._competitors is None and self._eventID != None:
            self._competitors = getAllPlayersInTournament(self._eventID)

        def _getCompetitorById(competitor_id: str):
            for c in self._competitors:
                if c["id"] == competitor_id:
                    return c
            return None

        for m in self._matches:
            for slot in m["slots"]:
                if not slot["playerID"].startswith("bye"):
                    _competitor = _getCompetitorById(slot["playerID"])
                    slot["gscrl_player_name"] = _competitor["name"]
                    slot["gscrl_wlt"] = {
                        "w": _competitor["wins"],
                        "l": _competitor["losses"],
                        "t": _competitor["ties"],
                    }

        return _matches

    def withFilter(self, filterFunction: Callable):
        matches = deepcopy(self._matches)
        matches = [x for x in matches if filterFunction(x)]

        return Matches(self._eventID, matches)

    def inOrder(self, orderFilter: Callable):
        return

    def withoutByes(self):
        _matches = deepcopy(self._matches)
        for m in _matches:
            m["slots"] = [c for c in m["slots"] if not c["playerID"].startswith("bye")]

        return Matches(self._eventID, matches=_matches)

    def toFile(self, path: str):
        with open(Path(path), "w") as output:
            output.write(json.dumps(self._matches, indent=4))

    def extends(self, event2: Self):
        matches = deepcopy(self._matches)
        if event2._matches not in [None, []]:
            for m2 in event2._matches:
                if "tournamentID" in m2:
                    matches.append(m2)

        new_matches = Matches(None, matches=matches)
        if self._eventID != event2._eventID:
            new_matches._multiple_tournaments = True

        return new_matches


class TrueFinals:
    def __init__(self):
        if "truefinals" in arena_settings:
            api_key = arena_settings.truefinals.api_key
            user_id = arena_settings.truefinals.user_id
            self._credentials = {"user_id": user_id, "api_key": api_key}

    def getAllPlayersOfTournament(self, tournamentID: str) -> list[dict]:
        players = getAllPlayersInTournament(self._credentials, tournamentID)
        return players

    def getAllMatches(self, tournamentID: str, weightclass: str=None) -> Matches:
        matches = Matches(eventID=tournamentID, weightclass=weightclass)
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
