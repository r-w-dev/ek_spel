import os

from flask import Flask

from flask_model import db
from poule import PouleDatabase
from ranking import TopUsers
from upload import UploadTeams, UploadGames, UploadUsers


app = Flask(__name__)
app.config["DEBUG"] = True

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    UploadTeams(recreate=False).upload()
    UploadGames(recreate=False).upload()
    UploadUsers(recreate=False).upload()


@app.route("/")
def hello_world():
    return "<p>Hello, World! from git</p>"


@app.route("/topusers")
def topusers():
    return TopUsers().to_html()


@app.route("/poules")
def poules():
    return PouleDatabase().add_all().to_html(col_space=16)
