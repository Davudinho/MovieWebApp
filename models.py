from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', backref='user', lazy=True)


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
