from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


from models import *


@app.route("/")
def home():
    return "Trekking Management Application"


if __name__ == "__main__":
    app.run(debug=True)