from config import settings as arena_settings
from truefinals_api.cached_wrapper import getAllTournamentsMatches
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

import json
import time

while True:
    ata_stuff = getAllTournamentsMatches()
    time.sleep(1)


data_stuff = [x for x in data_stuff if x["resultAnnotation"] != "BY"]
print(len(data_stuff))

# with open("new_cached_files.json", "w") as temporary_boi:
#    temporary_boi.write(json.dumps(data_stuff, indent=2))
