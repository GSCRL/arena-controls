from flask import Blueprint, render_template, request

from config import settings as arena_settings
from truefinals_api.wrapper import TrueFinals
from util.wrappers import ac_render_template

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
    show_header = request.args.get("show_header")
    matches = (
        truefinals.getCrossDivisionMatches(arena_settings.tournament_keys)
        .withoutByes()
        .withFilter(lambda x: x["state"] in ["called", "ready", "active"])
        .inOrder(
            lambda x: (
                x["calledSince"] or float(0),
                reversor(x["state"] == "unavailable"),
            ),
            reverse=False,
        )
        .done()
    )

    return ac_render_template(
        "upcoming_matches.html",
        div_matches=matches,
        autoreload=autoreload,
        show_header=show_header,
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

    return ac_render_template(
        "last_matches.html",
        div_matches=matches,
        autoreload=autoreload,
        event_name=arena_settings.event_name,
    )


@match_results.errorhandler(500)
def internal_error(error):
    autoreload = request.args.get("autoreload")
    return render_template(
        "base.html",
        autoreload=autoreload,
        errormsg="Sorry, this page has produced an error while generating.  Please try again in 30s.",
    )
