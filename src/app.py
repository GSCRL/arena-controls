from flask import Flask, render_template
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
    upcoming_matches = []
    for t in robotEvent.tournaments:
        temp_event_div = truefinals.getUpcomingMatchesWithPlayers(t["id"])
        # TODO Add in spot here to append the hardcoded division name for the upcoming matches screen.
        upcoming_matches.extend(temp_event_div)
    return render_template("upcoming.html", upcoming_matches=upcoming_matches)


@socketio.on("timer_event")
def handle_message(timer_data):
    emit("timer_event", timer_data, broadcast=True)


@socketio.on("timer_bg_event")
def handle_message(timer_bg_data):
    emit("timer_bg_event", timer_bg_data, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
