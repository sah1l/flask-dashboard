from app import app


@app.route('/')
@app.route('/index')
def index():
    return "<h1 style='color:blue'>Index page</h1>"



