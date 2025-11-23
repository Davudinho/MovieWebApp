import os
from flask import Flask, render_template, request, redirect, url_for
from data_manager import DataManager
from models import db

# Flask-App erstellen
app = Flask(__name__)

# Pfad für die SQLite-Datenbank definieren
basedir = os.path.abspath(os.path.dirname(__file__))

# Data-Ordner erstellen, falls er nicht existiert
data_dir = os.path.join(basedir, 'data')
os.makedirs(data_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy mit Flask verbinden
db.init_app(app)

# DataManager-Objekt erstellen
data_manager = DataManager()


# ==================== NUTZER-ROUTEN ====================

@app.route('/')
def index():
    """Startseite - Liste aller Nutzer"""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Neuen Nutzer hinzufügen"""
    name = request.form.get('name')
    data_manager.create_user(name)
    return redirect(url_for('index'))


# ==================== FILM-ROUTEN ====================

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """Filmliste eines bestimmten Nutzers anzeigen"""
    user = data_manager.get_user(user_id)
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Neuen Film zur Favoritenliste eines Nutzers hinzufügen"""
    title = request.form.get('title')
    data_manager.add_movie(user_id, title)
    return redirect(url_for('get_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Filmtitel bearbeiten"""
    new_title = request.form.get('title')
    data_manager.update_movie(movie_id, new_title)
    return redirect(url_for('get_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Film aus der Liste entfernen"""
    data_manager.delete_movie(movie_id)
    return redirect(url_for('get_movies', user_id=user_id))


# ==================== HAUPTPROGRAMM ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Erstellt alle Tabellen
    app.run(debug=True)
