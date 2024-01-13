from truefinals_api.api import (
    getAllGamesWithOneOrMoreCompetitors,
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
        match["slots"] = [x for x in match["slots"] if x["playerID"] is not None]
        for slot in match["slots"]:
            if slot["playerID"] != None:
                player_backfill = _playerIDToName(competitors, slot["playerID"])

                if "bye" in player_backfill:
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
                logging.warn(
                    "User did not enter tokens yet, cannot access API.  Please change apicreds.json"
                )

        self._credentials = json.loads(open(q, "r").read())

    def getGamesWithNonZeroCompetitors(self, tournamentID: str) -> list[dict]:
        return getAllGamesWithOneOrMoreCompetitors(self._credentials, tournamentID)

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

    def getMatchesInOrder(self, division_matches: list):
        def _sortHelper(q):
            # The match name is in the format of (division):(round)-(match), ie: "W:1-1".
            return (
                q['weightclass'],
                q["division"]["name"].split(":")[0], #bracketside, winners vs losers
                q["division"]["name"].split(":")[-1].split("-")[0], #round index
                q["division"]["name"].split(":")[-1].split("-")[-1], #match index
            )

        pprint(division_matches)
        # TODO SORT MATCHES PROPERLY IDFK
        #return sorted(division_matches, key=_sortHelper, reverse=True)
        # We need to flatten and unfuck this nightmarecode.  Please help.

      
        return division_matches

    def getAllFinishedCrossDivMatches(self, divisions):
        last_crossdiv_matches = []
        for t in divisions:
            temp_event_div = self.getFinishedMatches(t["id"])
            last_crossdiv_matches.append(
                {"weightclass": t["weightclass"], "division": temp_event_div}
            )

        return self.getMatchesInOrder(last_crossdiv_matches)

    def getAllUnfinishedCrossDivMatches(self, divisions):
        last_crossdiv_matches = []
        for t in divisions:
            temp_event_div = self.getUnfinishedMatches(t["id"])
            last_crossdiv_matches.append(
                {"weightclass": t["weightclass"], "division": temp_event_div}
            )

        return self.getMatchesInOrder(last_crossdiv_matches)
