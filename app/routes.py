from flask import url_for, redirect

from app import app


@app.route('/')
def index():
    return redirect(url_for("auth.login"))
