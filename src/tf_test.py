from config import settings as arena_settings
from pprint import pprint
import time

from truefinals_api.cached_api import (
    getAllGames,
    getAllPlayersInTournament,
    getEventInformation,
)

tourneys = [x["id"] for x in arena_settings["tournament_keys"]]

while True:
    for item in tourneys:
        make_wrapped = getAllPlayersInTournament(item)
        continuing_on = getAllGames(item)
        and_some_more = getEventInformation(item)
