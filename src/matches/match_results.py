from flask import Blueprint, render_template, request

from config import settings as arena_settings
from truefinals_api.wrapper import TrueFinals

match_results = Blueprint(
    "match_results", __name__, static_folder="./static", template_folder="./templates"
)

truefinals = TrueFinals()


class reversor:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


@match_results.route("/upcoming")
def routeForUpcomingMatches():
    autoreload = request.args.get("autoreload")
    matches = (
        truefinals.getCrossDivisionMatches(arena_settings.tournament_keys)
        .withoutByes()
        .withFilter(lambda x: x["state"] != "done")
        .withFilter(lambda x: len(x["slots"]) != 0)
        .inOrder(
            lambda x: (
                x["availableSince"] or float("inf"),
                reversor(x["bracketID"]),
                x["round"],
                x["state"],
            )
        )
        .done()
    )

    return render_template(
        "upcoming_matches.html",
        div_matches=matches,
        autoreload=autoreload,
        event_name=arena_settings.event_name,
    )


@match_results.route("/completed")
def routeForLastMatches():
    autoreload = request.args.get("autoreload")

    matches = (
        truefinals.getCrossDivisionMatches(arena_settings.tournament_keys)
        .withoutByes()
        .withFilter(lambda x: x["state"] == "done")
        .withFilter(lambda x: len(x["slots"]) != 0)
        .backfillResultStrings()
        .done()
    )

    return render_template(
        "last_matches.html",
        div_matches=matches,
        autoreload=autoreload,
        event_name=arena_settings.event_name,
    )
