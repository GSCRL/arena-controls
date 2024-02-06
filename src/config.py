import logging

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["event.json", ".secrets.json"],
)


def mandateConfig():
    logging.info("Running initial configuration assertion.")

    if "tournament_cages" not in settings:
        logging.warning("No event cages / locations set, assuming new event.")
        settings["tournament_cages"] = []

    if "tournament_keys" not in settings:
        logging.warning("No event divisions set, assuming new event.")
        settings["tournament_keys"] = []

    if "event_name" not in settings:
        logging.warning("No event name set, assuming new event with empty name.")
        settings["event_name"] = ""

    if "event_league" not in settings:
        logging.info("No league name set, assuming None.")
        settings["event_league"] = None  # Empty by default, fine.


mandateConfig()


def getCages():
    if "tournament_cages" not in settings:
        settings["tournament_cages"] = []

    return settings["tournament_cages"]


def addCage(cageName: str = None, cageID: int = None):
    if "tournament_cages" not in settings:
        settings["tournament_cages"] = []

    def _getHighestCage():
        max = -1
        for cage in settings["tournament_cages"]:
            if "id" in cage:
                if cage["id"] > max:
                    max = cage["id"]

        return max

    if cageName is None:
        settings["tournament_cages"].append(
            {"name": f"Cage {_getHighestCage()+1}", "id": cageID + 1}
        )
    else:
        settings["tournament_cages"].append({"name": f"{cageName}", "id": cageID + 1})
