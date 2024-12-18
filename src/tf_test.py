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

output = []

for match in matches_list:
    output.append(
        {
            "match_key": match["id"],
            "tournament_key": match["tournamentID"],
            "players": [
                getPlayerByIds(match["tournamentID"], player["playerID"])
                for player in match["slots"]
            ],
        }
    )

pprint(output)
