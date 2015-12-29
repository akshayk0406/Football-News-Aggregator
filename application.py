import os
from flask import Flask, render_template, send_from_directory, request

# initialization
app = Flask(__name__)

app.config.update(
    DEBUG = True,
)

# controllers

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.route("/")
def index():
    return 'Hello World' 

# launch
if __name__ == "__main__":
    app.run()

