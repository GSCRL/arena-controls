from api import (
    getAllGamesWithOneOrMoreCompetitors,
    getAllPlayersInTournament,
    getAllTourneys,
)
import json
from pathlib import Path
from pprint import pprint
import time

with open(Path("./apicreds.json"), "r") as file:
    credentials = json.loads(file.read())

tourneys = getAllTourneys(credentials)
games = getAllGamesWithOneOrMoreCompetitors(credentials, "e8e234ac02b34e77")
players = getAllPlayersInTournament(credentials, "e8e234ac02b34e77")

pprint(games)
pprint(players)
