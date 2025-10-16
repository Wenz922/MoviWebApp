from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from models import db, User, Movie
from data_manager import DataManager

import os
import requests

load_dotenv()

# Create the app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Link the database and the app.

data_manager = DataManager() # Create an object of DataManager class

OMDB_API_KEY = os.getenv('API_KEY')
OMDB_URL = "http://www.omdbapi.com/"
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

@app.route('/')
def home():
    """Home page: show all users and a form to add new users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    name = request.form.get('name', "").strip()
    try:
        data_manager.create_user(name)
        flash(f"User {name} created successfully!")
    except ValueError as e:
        flash(f"Error occurred while creating user {name}: {e}")
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def user_movies(user_id):
    """Show all favorite movies for a user."""
    user = User.query.get_or_404(user_id)
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', movies=movies, user=user)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """
    Fetch OMDb info for a movie title,
    Add this movie to a user’s list of favorite movies
    """
    title = request.form.get('title', "").strip()
    if not title:
        flash("Movie title is required!")
        return redirect(url_for('user_movies', user_id=user_id))

    if not OMDB_API_KEY:
        flash("OMDb API key is missing!")
        return redirect(url_for('user_movies', user_id=user_id))

    try:
        year = request.form.get('year', "").strip()
        params = {"apikey": OMDB_API_KEY, "t": title}
        if year:
            params["y"] = year

        res = requests.get(OMDB_URL, params=params)
        data = res.json()
        if data.get("Response") == "False":
            flash(f"Movie '{title}' not found.")
            return redirect(url_for('user_movies', user_id=user_id))

        # Create a new Movie ORM object
        movie = Movie(
            title=data.get("Title"),
            director=data.get("Director"),
            year=data.get("Year"),
            rating=float(data.get("imdbRating")) if data.get("imdbRating") != "N/A" else 0,
            poster_url=(None if data.get("Poster") in (None, "N/A") else data.get("Poster")),
            user_id=user_id
        )

        data_manager.add_movie(movie)
        flash(f"Movie '{movie.title}' added successfully!")

    except Exception as e:
        flash(f"Error occurred while adding movie: {e}")

    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Modify the movie rating and/or notes in a user’s list, without depending on OMDb for corrections."""
    rating = request.form.get('rating')
    notes = request.form.get('notes', "").strip()

    try:
        data_manager.update_movie(movie_id, rating, notes)
        flash(f"Movie '{movie_id}' updated successfully!")
    except Exception as e:
        flash(f"Error occurred while updating movie '{movie_id}': {e}")

    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a specific movie from a user’s favorite movie list."""
    try:
        data_manager.delete_movie(movie_id)
        flash(f"Movie '{movie_id}' deleted successfully!")
    except Exception as e:
        flash(f"Error occurred while deleting movie '{movie_id}': {e}")

    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
