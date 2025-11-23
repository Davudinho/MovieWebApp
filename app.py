import os
from flask import Flask
from data_manager import DataManager
from models import db, Movie

# Flask-App erstellen
app = Flask(__name__)

# Pfad für die SQLite-Datenbank definieren
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy mit Flask verbinden
db.init_app(app)

# DataManager-Objekt erstellen
data_manager = DataManager()


# Test-Route definieren
@app.route('/')
def home():
    return "Welcome to MoviWeb App!"


# Hauptprogramm: Datenbank erstellen und Flask-Server starten
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Erstellt alle Tabellen, falls noch nicht vorhanden
    app.run()
