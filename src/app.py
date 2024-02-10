from flask import Flask, render_template, request
from flask_caching import Cache
from flask_socketio import SocketIO, emit, join_room

from config import settings as arena_settings
from screens.user_screens import user_screens
from truefinals_api.wrapper import TrueFinals

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix="/screens")

app.config["SECRET_KEY"] = "secret secret key (required)!"
socketio = SocketIO(app)

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(app)

truefinals = TrueFinals()


@app.route("/")
def index():
    return render_template("base.html", title="Landing Page")


@app.route("/control")
def realTimer():
    return render_template("ctimer.html", user_screens=user_screens, title="Controller")


class reversor:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


@app.route("/settings", methods=("GET", "POST"))
def generateSettingsPage():
    if request.method == "GET":
        return render_template("app_settings.html", arena_settings=arena_settings)


@app.route("/upcoming")
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


@app.route("/lastmatches")
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


@socketio.on("timer_event")
def handle_message(timer_data):
    emit("timer_event", timer_data, broadcast=True)


@socketio.on("test_connect")
def handle_message(timer_data):
    emit("test_connect", broadcast=True)


@socketio.on("timer_bg_event")
def handle_message(timer_bg_data):
    emit("timer_bg_event", timer_bg_data, broadcast=True)


@socketio.on("join_cage_request")
def join_cage_handler(request_data: dict):
    if "cage_id" in request_data:
        join_room(f'cage_no_{request_data["cage_id"]}')
        emit("client_joined_room", f'cage_no_{request_data["cage_id"]}')


@socketio.on("player_ready")
def handle_message(ready_msg: dict):
    if type(ready_msg) == type(""):
        print(f"player_ready, {ready_msg}")
        emit("control_player_ready_event", {"station": ready_msg}, broadcast=True)

    elif ready_msg["pathname"].endswith(("red", "blue")):
        which_station = ready_msg["pathname"].split("/")[-1]
        print(f"player_ready, {which_station}")
        emit("control_player_ready_event", {"station": which_station}, broadcast=True)


@socketio.on("player_tapout")
def handle_message(tapout_msg: dict):
    if tapout_msg["pathname"].endswith(("red", "blue")):
        which_station = tapout_msg["pathname"].split("/")[-1]
        print(f"player_tapout, {which_station}")
        emit("control_player_tapout_event", {"station": which_station}, broadcast=True)


@socketio.on("reset_screen_states")
def handle_message():
    emit("reset_screen_states", broadcast=True)


@app.errorhandler(500)
def internal_error(error):
    autoreload = request.args.get("autoreload")
    return render_template(
        "base.html",
        autoreload=autoreload,
        errormsg="Sorry, this page has produced an error while generating.  Please try again in 30s.",
    )


import logging

logging.basicConfig(level="INFO")
# logging.basicConfig(level="WARNING")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
