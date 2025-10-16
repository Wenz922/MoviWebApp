from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database instance
db = SQLAlchemy()

# User model
class User(db.Model):
    __tablename__ = 'users'
    pass


# Movie model
class Movie(db.Model):
    __tablename__ = 'movies'
    pass
