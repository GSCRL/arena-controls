from flask import Flask, render_template
from config import settings as arena_settings, secrets as arena_secrets


def ac_render_template(template: str, **kwargs):
    # print(*args, **kwargs)
    # We inject the arena templates so that we don't need to manually pass them around.
    return render_template(
        template, arena_secrets=arena_secrets, arena_settings=arena_settings, **kwargs
    )
