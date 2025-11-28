import os

class Config:
    # Chemins absolus pour PythonAnywhere
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')

    # Nouveaux fichiers de données pour le système avancé
    CAVALIERS_FILE = os.path.join(DATA_DIR, 'cavaliers.json')
    EQUIDES_FILE = os.path.join(DATA_DIR, 'equides.json')
    COURS_RECURRENTS_FILE = os.path.join(DATA_DIR, 'cours_recurrents.json')
    PLANNING_FILE = os.path.join(DATA_DIR, 'planning.json')
    DISPONIBILITES_FILE = os.path.join(DATA_DIR, 'disponibilites.json')
    STATISTIQUES_FILE = os.path.join(DATA_DIR, 'statistiques.json')

    # Configuration serveur
    DEBUG = True  # ⚠️ Mettre False en production sur PythonAnywhere
    HOST = '0.0.0.0'
    PORT = 4004

    @staticmethod
    def init_directories():
        """Créer les dossiers nécessaires s'ils n'existent pas"""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        print(f"✅ Dossier data créé/vérifié : {Config.DATA_DIR}")