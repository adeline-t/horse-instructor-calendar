from flask import Blueprint, jsonify, request
from services.data_service import DataService

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')

@stats_bp.route('', methods=['GET'])
def get_stats():
    """Récupérer les statistiques"""

    return jsonify({'error': str("not defined")}), 500
