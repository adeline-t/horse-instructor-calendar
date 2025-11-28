from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Optional
from services.data_service import DataService

disponibilites_bp = Blueprint('disponibilites', __name__, url_prefix='/api/disponibilites')

# Jours de la semaine valides
JOURS_VALIDES = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']


def _validate_heure(heure: str) -> bool:
    """Valider le format d'heure HH:MM"""
    try:
        datetime.strptime(heure, '%H:%M')
        return True
    except ValueError:
        return False


def _validate_creneau(creneau: dict) -> Optional[str]:
    """
    Valider un créneau horaire.
    Retourne un message d'erreur si invalide, None sinon.
    """
    if not isinstance(creneau, dict):
        return "Le créneau doit être un dictionnaire"

    if 'start' not in creneau or 'end' not in creneau:
        return "Le créneau doit contenir 'start' et 'end'"

    start = creneau.get('start', '').strip()
    end = creneau.get('end', '').strip()

    if not start or not end:
        return "Les heures de début et fin sont requises"

    if not _validate_heure(start):
        return f"Format d'heure de début invalide: {start}"

    if not _validate_heure(end):
        return f"Format d'heure de fin invalide: {end}"

    # Vérifier que end > start
    try:
        start_time = datetime.strptime(start, '%H:%M')
        end_time = datetime.strptime(end, '%H:%M')
        if end_time <= start_time:
            return "L'heure de fin doit être après l'heure de début"
    except ValueError:
        return "Erreur lors de la comparaison des heures"

    return None


def _format_label(start: str, end: str) -> str:
    """Formater un label d'affichage pour un créneau"""
    return f"{start.replace(':', 'h')} - {end.replace(':', 'h')}"


@disponibilites_bp.route('', methods=['GET'])
def get_disponibilites():
    """Récupérer toutes les plages de disponibilité (tous les jours)"""
    try:
        disponibilites = DataService.read_disponibilites()
        return jsonify(disponibilites)
    except Exception as e:
        print(f"❌ Erreur get_disponibilites: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des disponibilités'}), 500


@disponibilites_bp.route('/<string:jour>', methods=['GET'])
def get_disponibilites_jour(jour):
    """Récupérer les disponibilités pour un jour spécifique"""
    try:
        jour = jour.lower()
        if jour not in JOURS_VALIDES:
            return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400

        disponibilites = DataService.read_disponibilites()
        jour_creneaux = disponibilites.get(jour, [])

        return jsonify({
            'jour': jour,
            'creneaux': jour_creneaux,
            'total': len(jour_creneaux)
        })
    except Exception as e:
        print(f"❌ Erreur get_disponibilites_jour: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des disponibilités du jour'}), 500


@disponibilites_bp.route('', methods=['PUT'])
def save_disponibilites():
    """Sauvegarder/remplacer toutes les plages de disponibilité"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Validation basique
        if not isinstance(data, dict):
            return jsonify({'error': 'Les données doivent être un dictionnaire'}), 400

        # Valider chaque jour
        for jour, creneaux in data.items():
            jour_lower = jour.lower()

            if jour_lower not in JOURS_VALIDES:
                return jsonify({'error': f'Jour invalide: {jour}'}), 400

            if not isinstance(creneaux, list):
                return jsonify({'error': f'Les créneaux pour {jour} doivent être une liste'}), 400

            # Valider chaque créneau
            for i, creneau in enumerate(creneaux):
                error = _validate_creneau(creneau)
                if error:
                    return jsonify({'error': f'{jour} - Créneau {i+1}: {error}'}), 400

        # Normaliser les clés en minuscules
        normalized_data = {k.lower(): v for k, v in data.items()}

        # Sauvegarder
        if not DataService.write_disponibilites(normalized_data):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print("✅ Disponibilités sauvegardées avec succès")
        return jsonify({'success': True, 'disponibilites': normalized_data})

    except Exception as e:
        print(f"❌ Erreur save_disponibilites: {e}")
        return jsonify({'error': 'Erreur lors de la sauvegarde des disponibilités'}), 500


@disponibilites_bp.route('/<string:jour>', methods=['PUT'])
def update_jour_complet(jour):
    """Remplacer tous les créneaux d'un jour spécifique"""
    try:
        jour = jour.lower()
        if jour not in JOURS_VALIDES:
            return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Les créneaux doivent être fournis dans une clé 'creneaux'
        creneaux = data.get('creneaux', data)  # Accepter directement la liste ou dans 'creneaux'

        if not isinstance(creneaux, list):
            return jsonify({'error': 'Les créneaux doivent être une liste'}), 400

        # Valider chaque créneau
        for i, creneau in enumerate(creneaux):
            error = _validate_creneau(creneau)
            if error:
                return jsonify({'error': f'Créneau {i+1}: {error}'}), 400

        disponibilites = DataService.read_disponibilites()
        disponibilites[jour] = creneaux

        # Sauvegarder
        if not DataService.write_disponibilites(disponibilites):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Créneaux mis à jour pour {jour}: {len(creneaux)} créneaux")
        return jsonify({'success': True, 'jour': jour, 'creneaux': creneaux})

    except Exception as e:
        print(f"❌ Erreur update_jour_complet: {e}")
        return jsonify({'error': 'Erreur lors de la mise à jour du jour'}), 500


@disponibilites_bp.route('/<string:jour>/creneau', methods=['POST'])
def add_creneau_jour(jour):
    """Ajouter un créneau pour un jour spécifique"""
    try:
        jour = jour.lower()
        if jour not in JOURS_VALIDES:
            return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Validation du créneau
        error = _validate_creneau(data)
        if error:
            return jsonify({'error': error}), 400

        start = data['start'].strip()
        end = data['end'].strip()
        label = data.get('label', '').strip() or _format_label(start, end)

        disponibilites = DataService.read_disponibilites()

        # Initialiser le jour si nécessaire
        if jour not in disponibilites:
            disponibilites[jour] = []

        # Vérifier les chevauchements
        for creneau in disponibilites[jour]:
            existing_start = datetime.strptime(creneau['start'], '%H:%M')
            existing_end = datetime.strptime(creneau['end'], '%H:%M')
            new_start = datetime.strptime(start, '%H:%M')
            new_end = datetime.strptime(end, '%H:%M')

            # Chevauchement si: (start1 < end2) AND (start2 < end1)
            if (new_start < existing_end) and (existing_start < new_end):
                return jsonify({
                    'error': 'Ce créneau chevauche un créneau existant',
                    'message': f'Conflit avec {creneau["start"]} - {creneau["end"]}'
                }), 400

        # Créer le nouveau créneau
        nouveau_creneau = {
            'start': start,
            'end': end,
            'label': label
        }

        disponibilites[jour].append(nouveau_creneau)

        # Trier par heure de début
        disponibilites[jour].sort(key=lambda x: x['start'])

        # Sauvegarder
        if not DataService.write_disponibilites(disponibilites):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Créneau ajouté pour {jour}: {start} - {end}")
        return jsonify({
            'success': True,
            'jour': jour,
            'creneau': nouveau_creneau,
            'creneaux': disponibilites[jour]
        }), 201

    except Exception as e:
        print(f"❌ Erreur add_creneau_jour: {e}")
        return jsonify({'error': 'Erreur lors de l\'ajout du créneau'}), 500


@disponibilites_bp.route('/<string:jour>/creneau/<int:index>', methods=['PUT'])
def update_creneau_jour(jour, index):
    """Mettre à jour un créneau spécifique pour un jour"""
    try:
        jour = jour.lower()
        if jour not in JOURS_VALIDES:
            return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        disponibilites = DataService.read_disponibilites()

        if jour not in disponibilites:
            return jsonify({'error': f'Aucun créneau défini pour {jour}'}), 404

        creneaux = disponibilites[jour]

        if index < 0 or index >= len(creneaux):
            return jsonify({'error': f'Index de créneau invalide (0-{len(creneaux)-1})'}), 400

        # Validation du nouveau créneau
        error = _validate_creneau(data)
        if error:
            return jsonify({'error': error}), 400

        start = data['start'].strip()
        end = data['end'].strip()
        label = data.get('label', '').strip() or _format_label(start, end)

        # Vérifier les chevauchements (sauf avec lui-même)
        for i, creneau in enumerate(creneaux):
            if i == index:
                continue

            existing_start = datetime.strptime(creneau['start'], '%H:%M')
            existing_end = datetime.strptime(creneau['end'], '%H:%M')
            new_start = datetime.strptime(start, '%H:%M')
            new_end = datetime.strptime(end, '%H:%M')

            if (new_start < existing_end) and (existing_start < new_end):
                return jsonify({
                    'error': 'Ce créneau chevauche un créneau existant',
                    'message': f'Conflit avec {creneau["start"]} - {creneau["end"]}'
                }), 400

        # Mettre à jour
        creneaux[index] = {
            'start': start,
            'end': end,
            'label': label
        }

        # Trier par heure de début
        creneaux.sort(key=lambda x: x['start'])
        disponibilites[jour] = creneaux

        # Sauvegarder
        if not DataService.write_disponibilites(disponibilites):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Créneau mis à jour pour {jour} à l'index {index}")
        return jsonify({
            'success': True,
            'jour': jour,
            'creneaux': creneaux
        })

    except Exception as e:
        print(f"❌ Erreur update_creneau_jour: {e}")
        return jsonify({'error': 'Erreur lors de la mise à jour du créneau'}), 500


@disponibilites_bp.route('/<string:jour>/creneau/<int:index>', methods=['DELETE'])
def delete_creneau_jour(jour, index):
    """Supprimer un créneau pour un jour spécifique"""
    try:
        jour = jour.lower()
        if jour not in JOURS_VALIDES:
            return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400

        disponibilites = DataService.read_disponibilites()

        if jour not in disponibilites:
            return jsonify({'error': f'Aucun créneau défini pour {jour}'}), 404

        creneaux = disponibilites[jour]

        if index < 0 or index >= len(creneaux):
            return jsonify({'error': f'Index de créneau invalide (0-{len(creneaux)-1})'}), 400

        deleted = creneaux.pop(index)
        disponibilites[jour] = creneaux

        # Sauvegarder
        if not DataService.write_disponibilites(disponibilites):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Créneau supprimé pour {jour}: {deleted['start']} - {deleted['end']}")
        return jsonify({
            'success': True,
            'jour': jour,
            'deleted': deleted,
            'creneaux': creneaux
        })

    except Exception as e:
        print(f"❌ Erreur delete_creneau_jour: {e}")
        return jsonify({'error': 'Erreur lors de la suppression du créneau'}), 500



@disponibilites_bp.route('/jours', methods=['GET'])
def get_jours_valides():
    """Récupérer la liste des jours de la semaine valides"""
    return jsonify({
        'jours': JOURS_VALIDES
    })
