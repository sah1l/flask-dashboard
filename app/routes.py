from flask import url_for, redirect
from flask_login import current_user

from app import app


@app.route('/')
def index():
    return redirect(url_for("auth.login"))
