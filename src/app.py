from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from screens.user_screens import user_screens
from truefinals_api.api import (
    getAllGamesWithOneOrMoreCompetitors,
    getAllPlayersInTournament,
    getAllTourneys,
)
import json
from pathlib import Path

#Secret API credentials for TrueFinals.  Yay.
with open(Path("./apicreds.json"), "r") as file:
    credentials = json.loads(file.read())

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix="/screens")

app.config["SECRET_KEY"] = "secret secret key (required)!"
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("timer.html", user_screens=user_screens)


@app.route("/upcoming")
def routeForUpcomingMatches():
    tourneys = getAllTourneys(credentials)
    games = getAllGamesWithOneOrMoreCompetitors(credentials, "e8e234ac02b34e77")
    players = getAllPlayersInTournament(credentials, "e8e234ac02b34e77")

    return render_template("upcoming.html", tourneys=tourneys, games=games, players=players)


@socketio.on("timer_event")
def handle_message(timer_data):
    emit("timer_event", timer_data, broadcast=True)


@socketio.on("timer_bg_event")
def handle_message(timer_bg_data):
    emit("timer_bg_event", timer_bg_data, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
