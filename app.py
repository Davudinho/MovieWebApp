import os
from flask import Flask, render_template, request, redirect, url_for, flash
from data_manager import DataManager
from models import db

# Flask-App erstellen
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Für Flash-Messages

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


# ==================== ERROR HANDLER ====================

@app.errorhandler(404)
def page_not_found(e):
    """404-Fehlerseite"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500-Fehlerseite"""
    return render_template('500.html'), 500


# ==================== NUTZER-ROUTEN ====================

@app.route('/')
def index():
    """Startseite - Liste aller Nutzer"""
    try:
        users = data_manager.get_users()
        return render_template('index.html', users=users)
    except Exception as e:
        print(f"Fehler beim Laden der Nutzer: {e}")
        return render_template('500.html'), 500


@app.route('/users', methods=['POST'])
def create_user():
    """Neuen Nutzer hinzufügen"""
    try:
        name = request.form.get('name')
        if not name or name.strip() == '':
            flash('Bitte geben Sie einen Namen ein.', 'error')
            return redirect(url_for('index'))

        data_manager.create_user(name.strip())
        flash(f'Nutzer "{name}" erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Fehler beim Erstellen des Nutzers: {e}")
        flash('Fehler beim Hinzufügen des Nutzers.', 'error')
        return redirect(url_for('index'))


# ==================== FILM-ROUTEN ====================

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """Filmliste eines bestimmten Nutzers anzeigen"""
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return render_template('404.html'), 404

        movies = data_manager.get_movies(user_id)
        return render_template('movies.html', user=user, movies=movies)
    except Exception as e:
        print(f"Fehler beim Laden der Filme: {e}")
        return render_template('500.html'), 500


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Neuen Film zur Favoritenliste eines Nutzers hinzufügen"""
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return render_template('404.html'), 404

        title = request.form.get('title')
        if not title or title.strip() == '':
            flash('Bitte geben Sie einen Filmtitel ein.', 'error')
            return redirect(url_for('get_movies', user_id=user_id))

        movie = data_manager.add_movie(user_id, title.strip())
        if movie:
            flash(f'Film "{movie.name}" erfolgreich hinzugefügt!', 'success')
        else:
            flash('Film konnte nicht von OMDb gefunden werden, aber wurde als Basis hinzugefügt.', 'warning')

        return redirect(url_for('get_movies', user_id=user_id))
    except Exception as e:
        print(f"Fehler beim Hinzufügen des Films: {e}")
        flash('Fehler beim Hinzufügen des Films.', 'error')
        return redirect(url_for('get_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Filmtitel bearbeiten"""
    try:
        new_title = request.form.get('title')
        if not new_title or new_title.strip() == '':
            flash('Bitte geben Sie einen neuen Titel ein.', 'error')
            return redirect(url_for('get_movies', user_id=user_id))

        success = data_manager.update_movie(movie_id, new_title.strip())
        if success:
            flash('Film erfolgreich aktualisiert!', 'success')
        else:
            flash('Film nicht gefunden.', 'error')

        return redirect(url_for('get_movies', user_id=user_id))
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Films: {e}")
        flash('Fehler beim Aktualisieren des Films.', 'error')
        return redirect(url_for('get_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Film aus der Liste entfernen"""
    try:
        success = data_manager.delete_movie(movie_id)
        if success:
            flash('Film erfolgreich gelöscht!', 'success')
        else:
            flash('Film nicht gefunden.', 'error')

        return redirect(url_for('get_movies', user_id=user_id))
    except Exception as e:
        print(f"Fehler beim Löschen des Films: {e}")
        flash('Fehler beim Löschen des Films.', 'error')
        return redirect(url_for('get_movies', user_id=user_id))


# ==================== HAUPTPROGRAMM ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Erstellt alle Tabellen
    app.run(debug=True)
