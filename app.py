from flask import Flask
from config import Config
from services.data_service import DataService

# Importer les blueprints
from routes.pages import pages_bp
from routes.cavaliers import cavaliers_bp
from routes.equides import equides_bp
from routes.cours_recurrents import cours_recurrents_bp
from routes.disponibilites import disponibilites_bp
from routes.planning import planning_bp
from routes.stats import stats_bp

def create_app():
    """Créer et configurer l'application Flask"""
    app = Flask(__name__)

    # Initialiser les dossiers et fichiers
    Config.init_directories()

    # Enregistrer les blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(cavaliers_bp)
    app.register_blueprint(equides_bp)
    app.register_blueprint(cours_recurrents_bp)
    app.register_blueprint(disponibilites_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(stats_bp)

    return app

# Créer l'instance app pour Gunicorn
app = create_app()

if __name__ == '__main__':

    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )