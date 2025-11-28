from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from typing import Optional
from services.data_service import DataService

cours_recurrents_bp = Blueprint('cours_recurrents', __name__, url_prefix='/api/cours-recurrents')

# Jours de la semaine valides
JOURS_VALIDES = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']


def _validate_heure(heure: str) -> bool:
    """Valider le format d'heure HH:MM"""
    try:
        datetime.strptime(heure, '%H:%M')
        return True
    except ValueError:
        return False


def _validate_couleur(couleur: str) -> bool:
    """Valider le format de couleur hexadécimale"""
    import re
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', couleur))


@cours_recurrents_bp.route('', methods=['GET'])
def get_cours_recurrents():
    """Récupérer tous les cours récurrents"""
    try:
        cours = DataService.read_cours_recurrents()
        return jsonify(cours)
    except Exception as e:
        print(f"❌ Erreur get_cours_recurrents: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des cours récurrents'}), 500


@cours_recurrents_bp.route('/actifs', methods=['GET'])
def get_cours_recurrents_actifs():
    """Récupérer les cours récurrents actifs uniquement"""
    try:
        cours = DataService.get_cours_recurrents_actifs()
        return jsonify(cours)
    except Exception as e:
        print(f"❌ Erreur get_cours_recurrents_actifs: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des cours actifs'}), 500


@cours_recurrents_bp.route('', methods=['POST'])
def add_cours_recurrent():
    """Ajouter un nouveau cours récurrent"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Validation des champs requis
        required_fields = ['nom', 'jour', 'heure', 'duree']
        for field in required_fields:
            if not data.get(field) or (isinstance(data[field], str) and not data[field].strip()):
                return jsonify({'error': f'Le champ "{field}" est requis'}), 400

        nom = data['nom'].strip()
        jour = data['jour'].strip().lower()
        heure = data['heure'].strip()
        description = data.get('description', '').strip()
        couleur = data.get('couleur', '#90EE90').strip()

        # Validation du nom (longueur minimale)
        if len(nom) < 3:
            return jsonify({'error': 'Le nom doit contenir au moins 3 caractères'}), 400

        # Validation du jour
        if jour not in JOURS_VALIDES:
            return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400

        # Validation de l'heure
        if not _validate_heure(heure):
            return jsonify({'error': 'Format d\'heure invalide (HH:MM requis)'}), 400

        # Validation de la durée
        try:
            duree = int(data['duree'])
            if duree <= 0 or duree > 480:  # Max 8 heures
                return jsonify({'error': 'La durée doit être entre 1 et 480 minutes'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'La durée doit être un nombre entier'}), 400

        # Validation de la couleur
        if not _validate_couleur(couleur):
            return jsonify({'error': 'Format de couleur invalide (format hex #RRGGBB requis)'}), 400

        cours = DataService.read_cours_recurrents()

        # Vérifier les doublons (même nom, jour et heure)
        for c in cours:
            if (c.get('nom', '').lower() == nom.lower() and
                c.get('jour', '').lower() == jour and
                c.get('heure') == heure):
                return jsonify({'error': 'Un cours avec ce nom, jour et heure existe déjà'}), 400

        # Générer un nouvel ID
        new_id = max((c.get('id', 0) for c in cours), default=0) + 1

        # Créer le nouveau cours récurrent
        nouveau_cours = {
            'id': new_id,
            'nom': nom,
            'jour': jour,
            'heure': heure,
            'duree': duree,
            'description': description,
            'actif': data.get('actif', True),
            'couleur': couleur
        }
        cours.append(nouveau_cours)

        # Sauvegarder
        if not DataService.write_cours_recurrents(cours):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Cours récurrent ajouté: {nouveau_cours['nom']} - {nouveau_cours['jour']} {nouveau_cours['heure']} (ID {new_id})")
        return jsonify({'success': True, 'cours': nouveau_cours, 'all_cours': cours}), 201

    except Exception as e:
        print(f"❌ Erreur add_cours_recurrent: {e}")
        return jsonify({'error': 'Erreur lors de l\'ajout du cours récurrent'}), 500


@cours_recurrents_bp.route('/<int:cours_id>', methods=['PUT'])
def update_cours_recurrent(cours_id):
    """Mettre à jour un cours récurrent existant"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        cours = DataService.read_cours_recurrents()

        # Trouver le cours
        cours_index = None
        for i, c in enumerate(cours):
            if c.get('id') == cours_id:
                cours_index = i
                break

        if cours_index is None:
            return jsonify({'error': 'Cours récurrent non trouvé'}), 404

        # Mise à jour des champs avec validation
        if 'nom' in data:
            nom = data['nom'].strip()
            if len(nom) < 3:
                return jsonify({'error': 'Le nom doit contenir au moins 3 caractères'}), 400
            cours[cours_index]['nom'] = nom

        if 'jour' in data:
            jour = data['jour'].strip().lower()
            if jour not in JOURS_VALIDES:
                return jsonify({'error': f'Jour invalide. Valeurs autorisées: {", ".join(JOURS_VALIDES)}'}), 400
            cours[cours_index]['jour'] = jour

        if 'heure' in data:
            heure = data['heure'].strip()
            if not _validate_heure(heure):
                return jsonify({'error': 'Format d\'heure invalide (HH:MM requis)'}), 400
            cours[cours_index]['heure'] = heure

        if 'duree' in data:
            try:
                duree = int(data['duree'])
                if duree <= 0 or duree > 480:
                    return jsonify({'error': 'La durée doit être entre 1 et 480 minutes'}), 400
                cours[cours_index]['duree'] = duree
            except (ValueError, TypeError):
                return jsonify({'error': 'La durée doit être un nombre entier'}), 400

        if 'description' in data:
            cours[cours_index]['description'] = data['description'].strip()

        if 'couleur' in data:
            couleur = data['couleur'].strip()
            if not _validate_couleur(couleur):
                return jsonify({'error': 'Format de couleur invalide (format hex #RRGGBB requis)'}), 400
            cours[cours_index]['couleur'] = couleur

        if 'actif' in data:
            cours[cours_index]['actif'] = bool(data['actif'])

        # Vérifier les doublons après modification (sauf lui-même)
        nom_check = cours[cours_index].get('nom', '').lower()
        jour_check = cours[cours_index].get('jour', '').lower()
        heure_check = cours[cours_index].get('heure')

        for i, c in enumerate(cours):
            if i != cours_index:
                if (c.get('nom', '').lower() == nom_check and
                    c.get('jour', '').lower() == jour_check and
                    c.get('heure') == heure_check):
                    return jsonify({'error': 'Un cours avec ce nom, jour et heure existe déjà'}), 400

        # Sauvegarder
        if not DataService.write_cours_recurrents(cours):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Cours récurrent mis à jour: {cours[cours_index]['nom']} (ID {cours_id})")
        return jsonify({'success': True, 'cours': cours[cours_index], 'all_cours': cours})

    except Exception as e:
        print(f"❌ Erreur update_cours_recurrent: {e}")
        return jsonify({'error': 'Erreur lors de la mise à jour du cours récurrent'}), 500


@cours_recurrents_bp.route('/<int:cours_id>', methods=['DELETE'])
def delete_cours_recurrent(cours_id):
    """Supprimer un cours récurrent"""
    try:
        cours = DataService.read_cours_recurrents()

        # Trouver et supprimer le cours
        cours_index = None
        for i, c in enumerate(cours):
            if c.get('id') == cours_id:
                cours_index = i
                break

        if cours_index is None:
            return jsonify({'error': 'Cours récurrent non trouvé'}), 404

        deleted = cours.pop(cours_index)

        # Sauvegarder
        if not DataService.write_cours_recurrents(cours):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Cours récurrent supprimé: {deleted.get('nom')} (ID {cours_id})")
        return jsonify({'success': True, 'deleted': deleted, 'all_cours': cours})

    except Exception as e:
        print(f"❌ Erreur delete_cours_recurrent: {e}")
        return jsonify({'error': 'Erreur lors de la suppression du cours récurrent'}), 500


@cours_recurrents_bp.route('/generation', methods=['GET'])
def generer_cours_semaine():
    """
    Générer les cours pour une semaine donnée à partir des cours récurrents actifs.
    Query params:
    - date: date de début de semaine (YYYY-MM-DD), par défaut = lundi de la semaine courante
    """
    try:
        # Récupérer la date de début de semaine
        date_str = request.args.get('date')
        if date_str:
            try:
                date_debut = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Format de date invalide (YYYY-MM-DD requis)'}), 400
        else:
            # Si pas de date, utiliser le lundi de la semaine actuelle
            today = datetime.now().date()
            date_debut = today - timedelta(days=today.weekday())

        # Générer les cours via DataService
        cours_generes = DataService.generer_cours_semaine(date_debut)

        # Calculer la date de fin (dimanche)
        date_fin = date_debut + timedelta(days=6)

        return jsonify({
            'success': True,
            'date_debut': date_debut.strftime('%Y-%m-%d'),
            'date_fin': date_fin.strftime('%Y-%m-%d'),
            'cours': cours_generes,
            'total': len(cours_generes)
        })

    except Exception as e:
        print(f"❌ Erreur generer_cours_semaine: {e}")
        return jsonify({'error': 'Erreur lors de la génération des cours'}), 500


@cours_recurrents_bp.route('/jours', methods=['GET'])
def get_jours_valides():
    """Récupérer la liste des jours de la semaine valides"""
    return jsonify({
        'jours': JOURS_VALIDES
    })
