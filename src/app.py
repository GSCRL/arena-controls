import logging

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, rooms

from config import settings as arena_settings, secrets as arena_secrets
from matches.match_results import match_results
from screens.user_screens import user_screens
from truefinals_api.wrapper import TrueFinals

logging.basicConfig(level="INFO")

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

current_clients = {}

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///combat_robot_event.db"
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(user_screens, url_prefix="/screens")
app.register_blueprint(match_results, url_prefix="/matches")

app.config["SECRET_KEY"] = "secret secret key (required)!"
socketio = SocketIO(app)

truefinals = TrueFinals()


@app.route("/")
def index():
    return render_template(
        "base.html", title="Landing Page", arena_settings=arena_settings
    )


@app.route("/control/<int:cageID>")
def realTimer(cageID):
    return render_template(
        "ctimer.html",
        user_screens=user_screens,
        title="Controller",
        cageID=cageID,
        arena_settings=arena_settings,
    )


@app.route("/settings", methods=("GET", "POST"))
def generateSettingsPage():
    if request.method == "GET":
        return render_template("app_settings.html", arena_settings=arena_settings, arena_secrets=arena_secrets)


@app.route("/clients", methods=("GET", "POST"))
def _temp_clients_page():
    return jsonify(current_clients)


@socketio.on("connect")
def base_connection_handler():
    pass


@socketio.on("disconnect")
def disconnect_handler():
    if request.sid in current_clients:
        del current_clients[request.sid]
        print("Client removed via disconnection.")


# Wrapper to take note of clients as they connect/reconnect to store in above so we can keep track of their current page.
@socketio.on("exists")
def state_client_exists():
    print(dir(request))
    if request.sid not in current_clients:
        current_clients[request.sid] = request.remote_addr
        print(f"SID {request.sid} added to global store (IP is {request.remote_addr})")
        emit("arena_query_location", to=request.sid)


# Unfortunately not globally used yet, do not trust as a safety system yet.
@socketio.on("globalESTOP")
def global_safety_eSTOP():
    valid_rooms = [ctl_rooms for ctl_rooms in rooms()]
    for v in valid_rooms:
        emit("timer_event", to=v)
        emit("timer_bg_event", "red", to=v)

# Old global handler, should probably be moved to globally accessible timer area.
@socketio.on("timer_event")
def handle_message(timer_message):
    print(timer_message)
    emit(
        "timer_event", timer_message["message"], to=f"cage_no_{timer_message['cageID']}"
    )

@socketio.on("timer_bg_event")
def handle_message(timer_bg_data):
    print(timer_bg_data)
    emit("timer_bg_event", timer_bg_data, to=f"cage_no_{timer_bg_data['cageID']}")


@socketio.on("join_cage_request")
def join_cage_handler(request_data: dict):
    if "cage_id" in request_data:
        join_room(f'cage_no_{request_data["cage_id"]}')
        emit(
            "client_joined_room",
            f'cage_no_{request_data["cage_id"]}',
            to=f"cage_no_{request_data['cage_id']}",
        )
        logging.info(f"User SID ({request.sid}) has joined Cage #{request_data['cage_id']}")


@socketio.on("player_ready")
def handle_message(ready_msg: dict):
    logging.info(f"player_ready, {ready_msg} for room {[ctl_rooms for ctl_rooms in rooms()]}")
    logging.info(ready_msg)
    emit("control_player_ready_event", ready_msg, to=f"cage_no_{ready_msg['cageID']}")


@socketio.on("player_tapout")
def handle_message(tapout_msg: dict):
    logging.info(
        f"player_tapout, {tapout_msg} for room {[ctl_rooms for ctl_rooms in rooms()]}"
    )
    emit(
        "control_player_tapout_event", tapout_msg, to=f"cage_no_{tapout_msg['cageID']}"
    )


@socketio.on("reset_screen_states")
def handle_message(reset_data):
    emit("reset_screen_states", f"cage_no_{reset_data['cageID']}")


@app.errorhandler(500)
def internal_error(error):
    autoreload = request.args.get("autoreload")
    return render_template(
        "base.html",
        autoreload=autoreload,
        arena_settings=arena_settings,
        errormsg="Sorry, this page has produced an error while generating.  Please try again in 30s.",
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
