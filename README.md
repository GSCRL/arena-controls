# GSCRL Arena Controls

A work-in-progress tool to run the timers for matches for combat robotics, as well as some stream overlay stuff.

## Integrations

This tool right now polls TrueFinals, with the intent to also push to TrueFinals down the line.

There will also be the ability to import some data from RobotCombatEvents should there be a want / need for that.

## Needs

This system is written in python and managed with poetry.

To install you'll need python 3.7 or greater, then to install `pipx` per the install guide [here.](https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx)

Then, install poetry via the steps [here.](https://python-poetry.org/docs/)

Afterwards, you should `cd` to your install location, `poetry install`, and then `poetry shell`.

`cd` to the `src` folder, and then run `python app.py`

## Networking

Note: Please be sure to change your IP to something static for consistency with the timer clients for reconnects.

We typically use `192.168.10.250` and set the travel router to have a DNS override for that to `internal.gscrl.org`.

