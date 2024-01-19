from flask import Flask, render_template, request
from flask_caching import Cache
from flask_socketio import SocketIO, emit, join_room, leave_room

from event import EventConfig
from screens.user_screens import user_screens
from truefinals_api.wrapper import TrueFinals

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix="/screens")

app.config["SECRET_KEY"] = "secret secret key (required)!"
socketio = SocketIO(app)

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(app)

truefinals = TrueFinals()
robotEvent = EventConfig()


@app.route("/")
def index():
    return render_template("ctimer.html", user_screens=user_screens)


@app.route("/upcoming")
@cache.cached(timeout=29)
def routeForUpcomingMatches():
    autoreload = request.args.get("autoreload")

    upcoming_crossdiv_matches = truefinals.getAllUnfinishedCrossDivMatches(
        robotEvent.tournaments
    )

    numMatches = len(upcoming_crossdiv_matches)

    return render_template(
        "upcoming.html",
        div_matches=upcoming_crossdiv_matches,
        autoreload=autoreload,
        numMatches=numMatches,
        cages=[{"name": "Big Steel", "id": 1}, {"name": "Old Green", "id": 2}],
    )


@app.route("/lastmatches")
@cache.cached(timeout=29)
def routeForLastMatches():
    autoreload = request.args.get("autoreload")

    last_crossdiv_matches = truefinals.getAllFinishedCrossDivMatches(
        robotEvent.tournaments
    )

    numMatches = len(last_crossdiv_matches)

    return render_template(
        "last.html",
        div_matches=last_crossdiv_matches,
        autoreload=autoreload,
        numMatches=numMatches,
    )


@app.route("/judges")
def judgesScreen():
    return render_template("judges.html")


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


if __name__ == "__main__":
    socketio.run(app, host="192.168.8.250", port=80)
