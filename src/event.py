import json
from pathlib import Path


class EventConfig:
    def __init__(self):
        self._event_info = json.loads(open(Path("event.json")).read())
        self.name = self._event_info["event_name"]
        self.organizers = self._event_info["event_league"]
        self.tournaments = self._event_info["event_tournament_codes"]
        self.tournaments = [
            x for x in self.tournaments if "id" in x and "weightclass" in x
        ]
