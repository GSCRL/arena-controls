import json
import logging
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
        if self._matches is None and self._competitors is None:
            self._competitors = getAllPlayersInTournament(self._eventID)

        if self._eventID != None:
            for match in self._matches:
                # In the event the eventID is none, the tournamentID of a given match should be added to said construction.
                # If already present, skip it.  This allows merging of matches of multiple tournaments together fairly "easily".
                if "tournamentID" not in match:
                    match["tournamentID"] = self._eventID

                # Same logic to filter by weightclass in the output / render it.
                if "weightclass" not in match:
                    match["weightclass"] = self._weightclass

            self.backfillNames()
            self.backfillFriendlyPreviousSlotName()

        # This captures if an erroneous list is merged / combined, having a single tournamentID does not apply anymore.
        if self._multiple_tournaments:
            self._eventID = None

    def __repr__(self):
        q = {"tournamentID": self._eventID, "matches": self._matches}
        return json.dumps(q)[100:]

    def __str__(self):
        return f"match list with {len(self._matches)}"

    def __len__(self):
        return len(self._matches)

    def backfillResultStrings(self):
        self.backfillMatchOutcomes()
        self.backfillMatchWinner()
        self.backfillFriendlyPreviousSlotName()

        return self

    def backfillFriendlyPreviousSlotName(self) -> Self:
        # Used to turn the use of a match ID into the "friendly" name.
        def matchIDToName(self, matchID: str, tournamentID: str) -> str:
            for m in self._matches:
                if m["tournamentID"] == tournamentID:
                    if m["id"] == matchID:
                        return m["name"] if not None else m["id"]

        for m in self._matches:
            for comp in m["slots"]:
                comp["gscrl_friendly_previous_name"] = matchIDToName(
                    self, comp["prevGameID"], m["tournamentID"]
                )

        return self

    def backfillMatchOutcomes(self):
        def _mapping(q):
            value = q["resultAnnotation"]
            if value == "KO":
                return "Knockout"
            if value == "TO":
                return "Tapout"
            if value == "TKO":
                return "Technical Knockout"
            if value == "JD":
                return "Judge's Decision"
            if value == "FF":
                return "Forfeit"
            if value == "BY":
                return "Match Bye"  # Not normally used but included for enumeration reasons.
            if value in [
                "HLD",
                "T",
            ]:  # HLD is HOLD, for when a JD takes longer @ NHRL.  Still unsure what `T` is used for.
                return "UNKNOWN"

        for match in self._matches:
            match["result_string"] = ""
            if match["resultAnnotation"] != None:
                match["result_string"] = _mapping(match)

        return self

    def backfillMatchWinner(self):
        for match in self._matches:
            match_score_to_win = match["scoreToWin"]

            match["slots"] = sorted(match["slots"], key=lambda x: x["score"])
            for slot in match["slots"]:
                if slot["score"] >= match_score_to_win:
                    match["winner_name"] = slot["gscrl_player_name"]

            # Technically a match by forfeit has a score of -1, making this a bit complex.  This is fine (tm).
            if not "winner_name" in match:
                match["winner_name"] = match["slots"][0]["gscrl_player_name"]

        return self

    def backfillNames(self):
        if self._competitors != None and self._eventID != None:
            self._competitors = getAllPlayersInTournament(self._eventID)
            # print(type(self._competitors))
            # print(self._competitors)

        def _getCompetitorById(competitor_id: str):
            if self._competitors is None:
                self._competitors = getAllPlayersInTournament(self._eventID)
                logging.info(
                    f"Event {self._eventID} has no competitors, fetching from API."
                )

            for c in self._competitors:
                if (
                    type(c) != str
                ):  # Patch around empty API responses due to rate limiting and poor architecture on my part.
                    if c["id"] == competitor_id:
                        return c
            return {"name": ""}

        for m in self._matches:
            for slot in m["slots"]:
                if "playerID" in slot and slot["playerID"] != None:
                    if not slot["playerID"].startswith("bye"):
                        _competitor = _getCompetitorById(slot["playerID"])
                        slot["gscrl_player_name"] = _competitor["name"]
                        try:
                            slot["gscrl_wlt"] = {
                                "w": _competitor["wins"],
                                "l": _competitor["losses"],
                                "t": _competitor["ties"],
                            }
                        except:
                                slot["gscrl_wlt"] = {
                                "w": _-1,
                                "l": -1,
                                "t": -1,
                            }

        return self

    def withFilter(self, filterFunction: Callable):
        self._matches = [x for x in self._matches if filterFunction(x)]
        return self

    def inOrder(self, orderFilter: Callable, reverse=False):
        self._matches = sorted(self._matches, key=orderFilter, reverse=reverse)
        return self

    def withoutByes(self):
        self._matches = [m for m in self._matches if m["resultAnnotation"] != "BY"]

        return self

    def toFile(self, path: str):
        with open(Path(path), "w") as output:
            output.write(json.dumps(self._matches, indent=4))
        return self

    def done(self):
        return self

    def __add__(self, event2: Self):
        if self._eventID != event2._eventID:
            self._multiple_tournaments = True

        if event2._matches not in [None, []]:
            self._matches = self._matches + event2._matches
            self._competitors = self._competitors + event2._competitors

        return self

    def __radd__(self, other):
        return self


class TrueFinals:
    def __init__(self):
        if "truefinals" in arena_settings:
            api_key = arena_settings.truefinals.api_key
            user_id = arena_settings.truefinals.user_id
            self._credentials = {"user_id": user_id, "api_key": api_key}

    def getAllPlayersOfTournament(self, tournamentID: str) -> list[dict]:
        players = getAllPlayersInTournament(self._credentials, tournamentID)
        return players

    def getAllMatches(self, tournamentID: str, weightclass: str = None) -> Matches:
        matches = Matches(eventID=tournamentID, weightclass=weightclass)
        return matches

    def getCrossDivisionMatches(self, division_list: list) -> Matches:
        if len(division_list) == 0:
            logging.error(
                "No divisions included in configuration.  Please populate configuration."
            )
            return None

        _matches = sum(
            [
                self.getAllMatches(x["id"], x["weightclass"]).done()
                for x in division_list
            ]
        )

        return _matches.done()
