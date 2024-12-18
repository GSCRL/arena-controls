from pprint import pprint

from truefinals_api.cached_wrapper import (
    getAllTournamentsMatches,
)

# logging.basicConfig()
# logging.getLogger().setLevel(logging.INFO)


# while True:
matches_list = getAllTournamentsMatches()

matches_dict = {}

from truefinals_api.cached_wrapper import getPlayerByIds

for match in matches_list:
    for player in match["slots"]:
        q = getPlayerByIds(match["tournamentID"], player["playerID"])
        pprint(q["name"])

# ttr = getAllTournamentsPlayers()
# time.sleep(1)


# data_stuff = [x for x in data_stuff if x["resultAnnotation"] != "BY"]
# print(len(data_stuff))

# with open("new_cached_files.json", "w") as temporary_boi:
#    temporary_boi.write(json.dumps(ttr, indent=2))
