from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from models import db, User, Movie
from data_manager import DataManager

import os
import requests
import logging
from logging.handlers import RotatingFileHandler

# --- Flask Setup ---
load_dotenv()

# Create the app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

db.init_app(app)  # Link the database and the app.

data_manager = DataManager() # Create an object of DataManager class

OMDB_API_KEY = os.getenv('API_KEY')
OMDB_URL = "http://www.omdbapi.com/"

# --- Logging Configuration ---
if not os.path.exists('logs'):
    os.mkdir('logs')

log_file = os.path.join('logs', 'app.log')
handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] in %(module)s: %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info("🎬 Movie Web App started successfully.")


# --- Route Map ---
@app.route('/')
def home():
    """Home page: show all users and a form to add new users."""
    try:
        users = data_manager.get_users()
        app.logger.info("Loaded home page with %d users.", len(users))
        return render_template('index.html', users=users)
    except Exception as e:
        app.logger.error("Error loading home page: %s", e, exc_info=True)
        flash("Error while loading home page.")
        return render_template('index.html', users=[])


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    name = request.form.get('name', "").strip()
    try:
        data_manager.create_user(name)
        flash(f"User {name} created successfully!")
        app.logger.info("Created new user: %s", name)
    except ValueError as e:
        flash(str(e), "error")
        app.logger.warning("User creation failed: %s", e)
    except Exception as e:
        db.session.rollback()
        flash(f"Error occurred while creating user {name}: {e}")
        app.logger.error("Database error creating user '%s': %s", name, e, exc_info=True)
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def user_movies(user_id):
    """Show all favorite movies for a user."""
    try:
        user = User.query.get_or_404(user_id)
        movies = data_manager.get_movies(user_id)
        app.logger.info("Loaded movies for user '%s' (%d movies).", user.name, len(movies))
        return render_template('movies.html', movies=movies, user=user)
    except Exception as e:
        app.logger.error("Error loading movies for user %d: %s", user_id, e, exc_info=True)
        flash("Error while loading user's movies.")
        return redirect(url_for('home'))


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
        res.raise_for_status()
        data = res.json()
        if data.get("Response") == "False":
            flash(f"Movie '{title}' not found.")
            app.logger.warning("OMDb: Movie not found for title '%s'", title)
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
        app.logger.info("Added movie '%s' for user_id=%d", movie.title, user_id)

    except requests.RequestException as e:
        flash("Error connecting to OMDb API.")
        app.logger.error("OMDb request failed for '%s': %s", title, e, exc_info=True)
    except Exception as e:
        flash(f"Error occurred while adding movie: {e}")
        app.logger.error("Add movie failed: %s", e, exc_info=True)

    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Modify the movie rating and/or notes in a user’s list, without depending on OMDb for corrections."""
    rating = request.form.get('rating')
    notes = request.form.get('notes', "").strip()

    try:
        data_manager.update_movie(movie_id, rating, notes)
        flash(f"Movie '{movie_id}' updated successfully!")
        app.logger.info("Updated movie ID=%d (rating=%s, notes=%s)", movie_id, rating, notes)
    except ValueError as e:
        flash(str(e), "error")
        app.logger.warning("Invalid update for movie ID=%d: %s", movie_id, e)
    except Exception as e:
        flash(f"Error occurred while updating movie '{movie_id}': {e}")
        app.logger.error("Update movie failed for ID=%d: %s", movie_id, e, exc_info=True)

    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a specific movie from a user’s favorite movie list."""
    try:
        data_manager.delete_movie(movie_id)
        flash(f"Movie '{movie_id}' deleted successfully!")
        app.logger.info("Deleted movie ID=%d for user_id=%d", movie_id, user_id)
    except Exception as e:
        flash(f"Error occurred while deleting movie '{movie_id}': {e}")
        app.logger.error("Delete movie failed for ID=%d: %s", movie_id, e, exc_info=True)

    return redirect(url_for('user_movies', user_id=user_id))

# --- Error Handling ---
@app.errorhandler(404)
def page_not_found(error):
    """Return a custom 404 error."""
    app.logger.warning("404 Not Found: %s", error)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Return a custom 500 error."""
    app.logger.error("500 Internal Server Error: %s", error, exc_info=True)
    return render_template('500.html'), 500


# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
