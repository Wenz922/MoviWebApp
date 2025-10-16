from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database instance
db = SQLAlchemy()

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship to movies
    movies = db.relationship('Movie', backref='user', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<User {self.id}: {self.name}>"

    def __str__(self):
        return f"User: {self.name}"


# Movie model
class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)

    # user-editable fields
    rating = db.Column(db.Integer, nullable=True)  # 1-10
    notes = db.Column(db.Text, nullable=True)

    # Link Movie to User with foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Movie {self.id}: {self.title}>"

    def __str__(self):
        return f"Movie: {self.title} (Director - {self.director}, Year - {self.year})"
