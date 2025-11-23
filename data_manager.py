import os
import requests
from models import db, User, Movie


class DataManager:
    def __init__(self):
        # OMDb API Key aus Umgebungsvariable laden
        self.omdb_api_key = os.environ.get('OMDB_API_KEY', 'your_api_key_here')
        self.omdb_url = 'http://www.omdbapi.com/'

    def create_user(self, name):
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()

    def get_users(self):
        return User.query.all()

    def get_user(self, user_id):
        return User.query.get(user_id)

    def get_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def fetch_movie_from_omdb(self, title):
        """Holt Filmdaten von der OMDb API"""
        params = {
            'apikey': self.omdb_api_key,
            't': title  # Suche nach Titel
        }

        try:
            response = requests.get(self.omdb_url, params=params)
            data = response.json()

            if data.get('Response') == 'True':
                return {
                    'name': data.get('Title'),
                    'director': data.get('Director'),
                    'year': int(data.get('Year', 0)) if data.get('Year', '').isdigit() else None,
                    'poster_url': data.get('Poster') if data.get('Poster') != 'N/A' else None
                }
            else:
                return None
        except Exception as e:
            print(f"Fehler beim Abrufen von OMDb: {e}")
            return None

    def add_movie(self, user_id, title):
        """Fügt einen Film hinzu, nachdem OMDb-Daten abgerufen wurden"""
        movie_data = self.fetch_movie_from_omdb(title)

        if movie_data:
            new_movie = Movie(
                name=movie_data['name'],
                director=movie_data['director'],
                year=movie_data['year'],
                poster_url=movie_data['poster_url'],
                user_id=user_id
            )
        else:
            # Fallback: Film ohne OMDb-Daten hinzufügen
            new_movie = Movie(
                name=title,
                user_id=user_id
            )

        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def update_movie(self, movie_id, new_title):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.name = new_title
            db.session.commit()
            return True
        return False

    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False
