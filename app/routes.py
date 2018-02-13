from flask import url_for, redirect
from flask_login import current_user

from app import app


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('stats.show_today'))

    return redirect(url_for("auth.login"))
