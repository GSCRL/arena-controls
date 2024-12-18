from config import settings as arena_settings
from pprint import pprint
import time

from truefinals_api.cached_api import (
    getAllGames,
    getAllPlayersInTournament,
    getEventInformation,
)

tourneys = [x["id"] for x in arena_settings["tournament_keys"]]

for i in range(300):
    for item in tourneys:
        make_wrapped = getAllPlayersInTournament(item)
        time.sleep(1)
        continuing_on = getAllGames(item)
        time.sleep(1)
        and_some_more = getEventInformation(item)


from truefinals_api.cached_api import purge_API_Cache

purge_API_Cache()

    # pprint(make_wrapped)
