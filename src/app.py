from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from screens.user_screens import user_screens

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix='/screens')

app.config['SECRET_KEY'] = 'secret secret key (required)!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template("homepage.html", user_screens=user_screens)

@app.route('/upcoming')
def routeForUpcomingMatches():
    return render_template("upcoming.html", upcoming_matches=[])

@socketio.on('timer_event')
def handle_message(timer_data):
    print(f'match timer is set to {timer_data}')
    emit('timer_event', timer_data, broadcast=True)

   
if __name__ == '__main__':
    socketio.run(app)

