from SportoweSwiryAPI_app import create_app

app=create_app()

@app.route("/")
def index():
    return "Hello from flask!"