from flask import Flask, render_template
from screens.user_screens import user_screens

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(user_screens, url_prefix='/screens')

@app.route('/')
def index():
    return render_template("base.html")
