from models import db, User, Movie
from flask import current_app as app


class DataManager():
    """
    Handles all database operations using SQLAlchemy ORM.
    Responsible only for CRUD operations (no API fetching).
    """
    # --- User operations ---
    def create_user(self, name: str) -> User:
        """ Adds a new user to the database."""
        name = name.strip()
        if not name:
            raise ValueError("User name cannot be empty.")

        # Check if user already exits
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            raise ValueError(f"User '{name}' already exists.")

        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        app.logger.info("User created: %s", name)
        return new_user

    def get_users(self):
        """ Gets all users from database."""
        users = User.query.order_by(User.name.asc()).all()
        app.logger.info("Fetched %d users.", len(users))
        return users

    # --- Movie operations ---
    def get_movies(self, user_id: int):
        """ Gets all movies from a given user id."""
        movies = Movie.query.filter_by(user_id=user_id).order_by(Movie.title.asc()).all()
        app.logger.info("Fetched %d movies for user_id=%d", len(movies), user_id)
        return movies

    def add_movie(self, movie: Movie):
        """
        Adds a new movie to the Movie project,
        where the movie has user id assigned.
        """
        if not movie.title:
            raise ValueError("Movie title cannot be empty.")

        db.session.add(movie)
        db.session.commit()
        app.logger.info("Movie added: '%s' (user_id=%d)", movie.title, movie.user_id)
        return movie

    def update_movie(self, movie_id: int, rating: int = None, notes: str = None):
        """ Updates the personal rating and/or notes from a given movie id."""
        movie = Movie.query.get(movie_id)
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")

        # Validate and update
        if rating not in (None, ""):
            try:
                rating_value = float(rating)
            except ValueError:
                raise ValueError("Rating must be a number.")
            if rating_value < 1 or rating_value > 10:
                raise ValueError("Rating must be between 1 and 10.")
            movie.rating = rating_value
        if notes is not None:
            notes = notes.strip()
            movie.notes = notes if notes else None

        db.session.commit()
        app.logger.info("Movie updated: ID=%d (rating=%s, notes=%s)", movie_id, rating, notes)
        return movie

    def delete_movie(self, movie_id: int):
        """ Deletes a movie from the user's list."""
        movie = Movie.query.get(movie_id)
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")

        db.session.delete(movie)
        db.session.commit()
        app.logger.info("Movie deleted: '%s' (ID=%d)", movie.title, movie_id)

