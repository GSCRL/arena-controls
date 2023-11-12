from truefinals_api.api import (
    getAllGamesWithOneOrMoreCompetitors,
    getAllPlayersInTournament,
    getAllTourneys,
)
import json
from pathlib import Path


class TrueFinals:
    def __init__(self, credential_file_location="./apicreds.json"):
        self._credentials = json.loads(open(Path(credential_file_location)).read())

    def getGamesWithNonZeroCompetitors(self, tournamentID: str) -> list[dict]:
        return getAllGamesWithOneOrMoreCompetitors(self._credentials, tournamentID)

    def getAllPlayersOfTournament(self, tournamentID: str) -> list[dict]:
        return getAllPlayersInTournament(self._credentials, tournamentID)

    def getAllTournaments(self) -> list[dict]:
        return getAllTourneys(self._credentials)

    def getUpcomingMatchesWithPlayers(self, tournamentID: str) -> list[dict]:
        matches_nonzero = self.getGamesWithNonZeroCompetitors(tournamentID)
        competitors = self.getAllPlayersOfTournament(tournamentID)

        def playerIDToName(competitors, playerID: str):
            for c in competitors:
                if c["id"] == playerID:
                    return c

        for match in matches_nonzero:
            for slot in match["slots"]:
                if slot["playerID"] != None:
                    player_backfill = playerIDToName(competitors, slot["playerID"])
                    slot["gscrl_friendly_name"] = player_backfill["name"]
                    slot["gscrl_seed"] = player_backfill["seed"]
                    slot["gscrl_wlt"] = {}
                    slot["gscrl_wlt"]["w"] = player_backfill["wins"]
                    slot["gscrl_wlt"]["l"] = player_backfill["losses"]
                    slot["gscrl_wlt"]["t"] = player_backfill["ties"]

        return matches_nonzero
