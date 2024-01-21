from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["event.json", ".secrets.json"],
)


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
