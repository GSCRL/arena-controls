from flask import Blueprint, render_template, redirect

user_screens = Blueprint(
    "user_screens", __name__, static_folder="./static", template_folder="./templates"
)


@user_screens.route("/")
def index():
    return redirect("/")


@user_screens.route("/red")
def redScreen():
    return render_template(
        "horiz_timer.html", team_color="#b74444", team_color_name="red"
    )


@user_screens.route("/blue")
def blueScreen():
    return render_template(
        "horiz_timer.html", team_color="#1892ce", team_color_name="blue"
    )


@user_screens.route("/timer")
def timerScreen():
    return render_template("justtimer.html")


@user_screens.route("/timervertical/red")
def redScreenVertical():
    return render_template(
        "vert_timer.html", team_color="#b74444", team_color_name="red"
    )


@user_screens.route("/timervertical/blue")
def blueScreenVertical():
    return render_template(
        "vert_timer.html", team_color="#1892ce", team_color_name="blue"
    )


@user_screens.route("/judges")
def judgesScreen():
    return "This is an example app"
