from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

# URLs "propres"
@pages_bp.route('/')
def index():
    return render_template('index.html')

@pages_bp.route('/cavaliers')
def cavaliers_page():
    return render_template('cavaliers.html')

@pages_bp.route('/equides')
def equides_page():
    return render_template('equides.html')

@pages_bp.route('/heures')
def heures_page():
    # votre template actuel s’appelle heures-cavaliers.html
    return render_template('heures-cavaliers.html')

@pages_bp.route('/cours-recurrents')
def cours_recurrents_page():
    return render_template('cours-recurrents.html')

@pages_bp.route('/disponibilites')
def disponibilites_page():
    return render_template('disponibilites.html')

@pages_bp.route('/stats')
def stats_page():
    return render_template('stats.html')

# Alias .html (compat)
@pages_bp.route('/cavaliers.html')
def cavaliers_page_html():
    return render_template('cavaliers.html')

@pages_bp.route('/equides.html')
def equides_page_html():
    return render_template('equides.html')

@pages_bp.route('/heures-cavaliers.html')
def heures_page_html():
    return render_template('heures-cavaliers.html')

@pages_bp.route('/cours-recurrents.html')
def cours_recurrents_page_html():
    return render_template('cours-recurrents.html')

@pages_bp.route('/disponibilites.html')
def disponibilites_page_html():
    return render_template('disponibilites.html')

@pages_bp.route('/stats.html')
def stats_page_html():
    return render_template('stats.html')
