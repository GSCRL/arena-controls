from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from screens.user_screens import user_screens
from truefinals_api.wrapper import TrueFinals
from event import EventConfig

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix="/screens")

truefinals = TrueFinals()
robotEvent = EventConfig()

app.config["SECRET_KEY"] = "secret secret key (required)!"
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("timer.html", user_screens=user_screens)


@app.route("/upcoming")
def routeForUpcomingMatches():
    autoreload = request.args.get("autoreload")

    upcoming_crossdiv_matches = []
    for t in robotEvent.tournaments:
        temp_event_div = truefinals.getUpcomingMatchesWithPlayers(t["id"])
        upcoming_crossdiv_matches.append(
            {"weightclass": t["weightclass"], "division": temp_event_div}
        )

    print(upcoming_crossdiv_matches)
    return render_template(
        "upcoming.html", div_matches=upcoming_crossdiv_matches, autoreload=autoreload
    )


@socketio.on("timer_event")
def handle_message(timer_data):
    emit("timer_event", timer_data, broadcast=True)


@socketio.on("timer_bg_event")
def handle_message(timer_bg_data):
    emit("timer_bg_event", timer_bg_data, broadcast=True)


@socketio.on("player_ready")
def handle_message(ready_msg: dict):
    if ready_msg["pathname"].endswith(("red", "blue")):
        which_station = ready_msg["pathname"].split("/")[
            -1
        ]  # which team side readied up will be passed from the URL name.  This allows both timer variants to ready up trivially.
        print(f"player_ready, {which_station}")
        emit("control_player_ready_event", {"station": which_station}, broadcast=True)


@socketio.on("player_tapout")
def handle_message(tapout_msg: dict):
    if tapout_msg["pathname"].endswith(("red", "blue")):
        which_station = tapout_msg["pathname"].split("/")[
            -1
        ]  # which team side readied up will be passed from the URL name.  This allows both timer variants to ready up trivially.
        print(f"player_tapout, {which_station}")
        emit("control_player_tapout_event", {"station": which_station}, broadcast=True)


@socketio.on("reset_screen_states")
def handle_message():
    emit("reset_screen_states_event", broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
