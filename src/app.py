from flask import Flask, render_template
from screens.user_screens import user_screens

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix='/screens')

@app.route('/')
def index():
    return render_template("homepage.html", user_screens=user_screens)

@app.route('/upcoming')
def routeForUpcomingMatches():
    return render_template("upcoming.html", upcoming_matches=[])