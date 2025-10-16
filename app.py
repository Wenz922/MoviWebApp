from flask import Flask, render_template, request

from models import db, User, Movie
from data_manager import DataManager

import os

# Create the app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Link the database and the app.

data_manager = DataManager() # Create an object of your DataManager class

@app.route('/')
def home():
    return "Welcome to MoviWeb App!"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
