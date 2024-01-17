from truefinals_api.api import (
    getAllPlayersInTournament,
    getAllTourneys,
    getAllGames,
)
import json
from pathlib import Path
import logging
from pprint import pprint

"""Helper function to check whether the player is a legitimate player or to get a bye.

Terrible and only used for when the filtering to remove byes doesn't work."""


# HELPER FUNCTION
def _playerIDToName(competitors, playerID: str):
    for c in competitors:
        if c["id"] == playerID:
            return c
    if playerID.startswith("bye"):
        return {
            "name": "Bye",
            "seed": -1,
            "wins": -1,
            "losses": -1,
            "ties": -1,
            "bye": True,
        }
    logging.warning(f"did not find competitor, oops!  Was looking for {playerID}")


# HELPER FUNCTION
def _backfill_byes_plus_wlt(competitors, matches):
    for match in matches:
        match["slots"] = [
            x
            for x in match["slots"]
            if (x["playerID"] is not None) or (x["gameID"].startswith("GF"))
        ]  # This filter will exclude grand finals / "TrueFinals" matches, so we need to verify it's not a grand finals match and exclude it.
        for slot in match["slots"]:
            if slot["playerID"] != None:
                player_backfill = _playerIDToName(competitors, slot["playerID"])

                if (
                    "bye" in player_backfill
                ):  # If we want to show bye'd matches, this can be commented out.
                    match["has_bye"] = True

                slot["gscrl_friendly_name"] = player_backfill["name"]
                slot["gscrl_seed"] = player_backfill["seed"]
                slot["gscrl_wlt"] = {}
                slot["gscrl_wlt"]["w"] = player_backfill["wins"]
                slot["gscrl_wlt"]["l"] = player_backfill["losses"]
                slot["gscrl_wlt"]["t"] = player_backfill["ties"]

    matches = [x for x in matches if len(x["slots"]) != 0]

    return matches


class TrueFinals:
    def __init__(self, credential_file_location="./apicreds.json"):
        q = Path(credential_file_location)

        if not q.exists():
            q.touch()
            with open(q, "w") as fileitem:
                fileitem.write(json.dumps({"user_id": "", "api_key": ""}))
                logging.error(
                    "User did not enter tokens yet, cannot access API.  Please change apicreds.json"
                )

        self._credentials = json.loads(open(q, "r").read())

    def getAllPlayersOfTournament(self, tournamentID: str) -> list[dict]:
        return getAllPlayersInTournament(self._credentials, tournamentID)

    def getAllTournaments(self) -> list[dict]:
        return getAllTourneys(self._credentials)

    def getFinishedMatches(self, tournamentID: str) -> list[dict]:
        competitors = self.getAllPlayersOfTournament(tournamentID)
        matches = getAllGames(self._credentials, tournamentID)

        matches = _backfill_byes_plus_wlt(competitors, matches)

        matches = [x for x in matches if x["state"] == "done" and not ("has_bye" in x)]

        return matches

    def getUnfinishedMatches(self, tournamentID: str) -> list[dict]:
        competitors = self.getAllPlayersOfTournament(tournamentID)
        matches = getAllGames(self._credentials, tournamentID)

        matches = _backfill_byes_plus_wlt(competitors, matches)

        matches = [x for x in matches if x["state"] != "done" and not ("has_bye" in x)]
        return matches

    def getMatchesInOrder(self, cross_div_matches: list):
        flat_matches = []
        for div in cross_div_matches:
            for match in div["division"]:
                match["gscrl_weightclass"] = div["weightclass"]
                flat_matches.append(match)

        pprint(flat_matches)

        def _sortHelper(q):
            # This function is going to have to build the entire bracket out to find the "last match"
            #  and offset the match id proportionately to represent the order they're sorted in.
            # This is due to the need to finish at the same time, such that if one bracket is N
            # longer than another that one will be started N rounds later.

            # Yes it's messy, good luck.
            return (
                q["name"].split(":")[-1].split("-")[0],  # round index
                q["name"].split(":")[0],  # bracketside, winners vs losers
                q[
                    "gscrl_weightclass"
                ],  # weightclass name, used as a sort so we go in order between weightclasses even if the match numbers are the same.
                q["name"].split(":")[-1].split("-")[-1],  # match index
            )

        flat_matches = sorted(flat_matches, key=_sortHelper, reverse=False)
        # TODO SORT MATCHES PROPERLY, good luck.  See above comment.

        # flat_matches = sorted(flat_matches, key=lambda match: match['calledSince']  else 0, reverse=True)
        # Sort by the end time as well such thatr we can
        return flat_matches

    def getAllFinishedCrossDivMatches(self, divisions):
        last_crossdiv_matches = []
        for t in divisions:
            temp_event_div = self.getFinishedMatches(t["id"])
            last_crossdiv_matches.append(
                {"weightclass": t["weightclass"], "division": temp_event_div}
            )

        orderedMatches = self.getMatchesInOrder(last_crossdiv_matches)

        # We retrieve them in order for consistency
        # and re-order them based on the last published end-time to avoid having a mess with the exposure of it.
        # In the future the matches must be better represented / manipulated to expose to controls to simplify
        # posting of scores without Kirstin needing to spend copious amounts of time.

        return sorted(orderedMatches, key=lambda x: x["endTime"], reverse=True)

    def getAllUnfinishedCrossDivMatches(self, divisions):
        last_crossdiv_matches = []
        for t in divisions:
            temp_event_div = self.getUnfinishedMatches(t["id"])
            last_crossdiv_matches.append(
                {"weightclass": t["weightclass"], "division": temp_event_div}
            )

        return self.getMatchesInOrder(last_crossdiv_matches)
