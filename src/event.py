from pathlib import Path
import json


class EventConfig:
    def __init__(self):
        self._event_info = json.loads(open(Path("event.json")).read())
        self.name = self._event_info["event_name"]
        self.organizers = self._event_info["event_league"]
        self.tournaments = self._event_info["event_tournament_codes"]
