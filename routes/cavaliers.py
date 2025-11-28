from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Optional
from services.data_service import DataService

cavaliers_bp = Blueprint('cavaliers', __name__, url_prefix='/api/cavaliers')


def _validate_email(email: str) -> bool:
    """Valider format email basique"""
    email = email.strip()
    return '@' in email and '.' in email.split('@')[-1]


def _validate_phone(phone: str) -> bool:
    """Valider format téléphone français (10 chiffres)"""
    cleaned = phone.strip().replace(' ', '').replace('-', '').replace('.', '')
    return cleaned.isdigit() and len(cleaned) == 10


def _validate_date(date_str: str) -> Optional[datetime]:
    """Valider et parser une date ISO (YYYY-MM-DD)"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


@cavaliers_bp.route('', methods=['GET'])
def get_cavaliers():
    """Récupérer tous les cavaliers"""
    try:
        cavaliers = DataService.read_cavaliers()
        return jsonify(cavaliers)
    except Exception as e:
        print(f"❌ Erreur get_cavaliers: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des cavaliers'}), 500


@cavaliers_bp.route('/actifs', methods=['GET'])
def get_cavaliers_actifs():
    """Récupérer les cavaliers actifs pour une date donnée (ou aujourd'hui)"""
    try:
        date_str = request.args.get('date')
        if date_str:
            parsed = _validate_date(date_str)
            if not parsed:
                return jsonify({'error': 'Format de date invalide (YYYY-MM-DD requis)'}), 400
            target_date = parsed.date()
        else:
            target_date = datetime.now().date()

        cavaliers = DataService.get_cavaliers_actifs(at_date=target_date)
        return jsonify(cavaliers)
    except Exception as e:
        print(f"❌ Erreur get_cavaliers_actifs: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des cavaliers actifs'}), 500


@cavaliers_bp.route('/disponibles/<int:equide_id>', methods=['GET'])
def get_cavaliers_disponibles_pour_equide(equide_id):
    """
    Récupérer les cavaliers ayant accès à un équidé donné.
    Logique inverse: on cherche tous les cavaliers qui ont des heures sur cet équidé
    ou qui en sont propriétaires.
    """
    try:
        # Lire l'équidé
        equides = DataService.read_equides()
        equide = next((e for e in equides if e.get('id') == equide_id), None)
        if not equide:
            return jsonify({'error': 'Équidé non trouvé'}), 404

        cavaliers_actifs = DataService.get_cavaliers_actifs()
        disponibles = []

        proprietaire_id = equide.get('proprietaire_id')
        heures_map = equide.get('heures_par_cavalier', {}) or {}

        for cavalier in cavaliers_actifs:
            cid = cavalier.get('id')
            # Propriétaire ou a des heures allouées
            if (proprietaire_id is not None and cid == proprietaire_id) or str(cid) in heures_map:
                disponibles.append(cavalier)

        return jsonify(disponibles)
    except Exception as e:
        print(f"❌ Erreur get_cavaliers_disponibles_pour_equide: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des cavaliers disponibles'}), 500


@cavaliers_bp.route('', methods=['POST'])
def add_cavalier():
    """Ajouter un nouveau cavalier"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Validation des champs requis
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({'error': f'Le champ "{field}" est requis'}), 400

        name = data['name'].strip()
        email = data['email'].strip()
        phone = data['phone'].strip()

        # Validation email
        if not _validate_email(email):
            return jsonify({'error': 'Format d\'email invalide'}), 400

        # Validation téléphone
        if not _validate_phone(phone):
            return jsonify({'error': 'Format de téléphone invalide (10 chiffres requis)'}), 400

        # Validation des dates
        date_debut = data.get('date_debut', '').strip()
        date_fin = data.get('date_fin', '').strip()

        if date_debut and not _validate_date(date_debut):
            return jsonify({'error': 'Format de date de début invalide (YYYY-MM-DD)'}), 400

        if date_fin and not _validate_date(date_fin):
            return jsonify({'error': 'Format de date de fin invalide (YYYY-MM-DD)'}), 400

        if date_debut and date_fin:
            debut = _validate_date(date_debut)
            fin = _validate_date(date_fin)
            if debut and fin and fin.date() < debut.date():
                return jsonify({'error': 'La date de fin ne peut être antérieure à la date de début'}), 400

        # Validation des heures (doivent être des entiers >= 0)
        heures_forfait_co = data.get('heures_forfait_co', 0)
        heures_cours_part = data.get('heures_cours_part', 0)

        try:
            heures_forfait_co = int(heures_forfait_co)
            heures_cours_part = int(heures_cours_part)
            if heures_forfait_co < 0 or heures_cours_part < 0:
                return jsonify({'error': 'Les heures doivent être des nombres positifs'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Les heures doivent être des nombres entiers'}), 400

        cavaliers = DataService.read_cavaliers()

        # Vérifier si le cavalier existe déjà (nom case-insensitive)
        if any(c.get('name', '').lower() == name.lower() for c in cavaliers):
            return jsonify({'error': 'Ce cavalier existe déjà'}), 400

        # Générer nouvel ID
        new_id = max((c.get('id', 0) for c in cavaliers), default=0) + 1

        nouveau_cavalier = {
            'id': new_id,
            'name': name,
            'email': email,
            'phone': phone,
            'heures_forfait_co': heures_forfait_co,
            'heures_cours_part': heures_cours_part,
            'date_debut': date_debut if date_debut else '',
            'date_fin': date_fin if date_fin else '',
            'actif': data.get('actif', True),
            'notes': data.get('notes', '').strip()
        }
        cavaliers.append(nouveau_cavalier)

        if not DataService.write_cavaliers(cavaliers):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Cavalier ajouté: {nouveau_cavalier['name']} (ID {new_id})")
        return jsonify({'success': True, 'cavalier': nouveau_cavalier, 'cavaliers': cavaliers}), 201

    except Exception as e:
        print(f"❌ Erreur add_cavalier: {e}")
        return jsonify({'error': 'Erreur lors de l\'ajout du cavalier'}), 500


@cavaliers_bp.route('/<int:cavalier_id>', methods=['PUT'])
def update_cavalier(cavalier_id):
    """Mettre à jour un cavalier existant"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        cavaliers = DataService.read_cavaliers()

        # Trouver le cavalier
        cavalier_index = None
        for i, c in enumerate(cavaliers):
            if c.get('id') == cavalier_id:
                cavalier_index = i
                break

        if cavalier_index is None:
            return jsonify({'error': 'Cavalier non trouvé'}), 404

        # Mise à jour des champs avec validation
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({'error': 'Le nom doit contenir au moins 2 caractères'}), 400
            # Vérifier unicité (sauf pour lui-même)
            for i, c in enumerate(cavaliers):
                if i != cavalier_index and c.get('name', '').lower() == name.lower():
                    return jsonify({'error': 'Ce nom existe déjà'}), 400
            cavaliers[cavalier_index]['name'] = name

        if 'email' in data:
            email = data['email'].strip()
            if not _validate_email(email):
                return jsonify({'error': 'Format d\'email invalide'}), 400
            cavaliers[cavalier_index]['email'] = email

        if 'phone' in data:
            phone = data['phone'].strip()
            if not _validate_phone(phone):
                return jsonify({'error': 'Format de téléphone invalide (10 chiffres requis)'}), 400
            cavaliers[cavalier_index]['phone'] = phone

        if 'heures_forfait_co' in data:
            try:
                heures = int(data['heures_forfait_co'])
                if heures < 0:
                    return jsonify({'error': 'Les heures forfait CO doivent être positives'}), 400
                cavaliers[cavalier_index]['heures_forfait_co'] = heures
            except (ValueError, TypeError):
                return jsonify({'error': 'Les heures forfait CO doivent être un nombre entier'}), 400

        if 'heures_cours_part' in data:
            try:
                heures = int(data['heures_cours_part'])
                if heures < 0:
                    return jsonify({'error': 'Les heures cours particuliers doivent être positives'}), 400
                cavaliers[cavalier_index]['heures_cours_part'] = heures
            except (ValueError, TypeError):
                return jsonify({'error': 'Les heures cours particuliers doivent être un nombre entier'}), 400

        if 'date_debut' in data:
            date_debut = data['date_debut'].strip() if data['date_debut'] else ''
            if date_debut and not _validate_date(date_debut):
                return jsonify({'error': 'Format de date de début invalide (YYYY-MM-DD)'}), 400
            cavaliers[cavalier_index]['date_debut'] = date_debut

        if 'date_fin' in data:
            date_fin = data['date_fin'].strip() if data['date_fin'] else ''
            if date_fin and not _validate_date(date_fin):
                return jsonify({'error': 'Format de date de fin invalide (YYYY-MM-DD)'}), 400
            cavaliers[cavalier_index]['date_fin'] = date_fin

        if 'actif' in data:
            cavaliers[cavalier_index]['actif'] = bool(data['actif'])

        if 'notes' in data:
            cavaliers[cavalier_index]['notes'] = data['notes'].strip()

        # Validation cohérence des dates
        debut_str = cavaliers[cavalier_index].get('date_debut', '')
        fin_str = cavaliers[cavalier_index].get('date_fin', '')
        if debut_str and fin_str:
            debut = _validate_date(debut_str)
            fin = _validate_date(fin_str)
            if debut and fin and fin.date() < debut.date():
                return jsonify({'error': 'La date de fin ne peut être antérieure à la date de début'}), 400

        if not DataService.write_cavaliers(cavaliers):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Cavalier mis à jour: {cavaliers[cavalier_index]['name']} (ID {cavalier_id})")
        return jsonify({'success': True, 'cavalier': cavaliers[cavalier_index], 'cavaliers': cavaliers})

    except Exception as e:
        print(f"❌ Erreur update_cavalier: {e}")
        return jsonify({'error': 'Erreur lors de la mise à jour du cavalier'}), 500


@cavaliers_bp.route('/<int:cavalier_id>', methods=['DELETE'])
def delete_cavalier(cavalier_id):
    """Supprimer un cavalier (avec vérification des dépendances)"""
    try:
        cavaliers = DataService.read_cavaliers()

        # Vérifier dépendances: heures allouées
        heures = DataService.read_heures_cavaliers()
        if str(cavalier_id) in heures and heures[str(cavalier_id)]:
            return jsonify({
                'error': 'Ce cavalier a des heures allouées',
                'message': 'Veuillez d\'abord supprimer ou réattribuer ses heures d\'équitation'
            }), 400

        # Vérifier dépendances: équidés propriétaires
        equides = DataService.read_equides()
        owned = [e for e in equides if e.get('proprietaire_id') == cavalier_id]
        if owned:
            return jsonify({
                'error': 'Ce cavalier possède des équidés',
                'message': f'Équidés possédés: {", ".join(e.get("name", "Sans nom") for e in owned)}'
            }), 400

        # Vérifier dépendances: présence dans planning
        planning = DataService.read_planning()
        has_courses = False
        for semaine in planning.values():
            for jour in semaine.values():
                for creneau in jour.values():
                    for cours in creneau:
                        if cavalier_id in cours.get('cavaliers', []):
                            has_courses = True
                            break
                    if has_courses:
                        break
                if has_courses:
                    break
            if has_courses:
                break

        if has_courses:
            return jsonify({
                'error': 'Ce cavalier est inscrit à des cours',
                'message': 'Veuillez d\'abord le retirer des cours du planning'
            }), 400

        # Trouver et supprimer
        cavalier_index = None
        for i, c in enumerate(cavaliers):
            if c.get('id') == cavalier_id:
                cavalier_index = i
                break

        if cavalier_index is None:
            return jsonify({'error': 'Cavalier non trouvé'}), 404

        deleted = cavaliers.pop(cavalier_index)

        if not DataService.write_cavaliers(cavaliers):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Cavalier supprimé: {deleted.get('name')} (ID {cavalier_id})")
        return jsonify({'success': True, 'deleted': deleted, 'cavaliers': cavaliers})

    except Exception as e:
        print(f"❌ Erreur delete_cavalier: {e}")
        return jsonify({'error': 'Erreur lors de la suppression du cavalier'}), 500


@cavaliers_bp.route('/statistiques/mensuelles/<int:annee>/<int:mois>', methods=['GET'])
def get_statistiques_mensuelles_cavalier(annee, mois):
    """
    Obtenir les statistiques mensuelles pour tous les cavaliers actifs.
    Utilise DataService.calculer_statistiques_mois pour agréger les cours.
    """
    try:
        if not (1 <= mois <= 12):
            return jsonify({'error': 'Mois invalide (1-12)'}), 400

        # Récupérer les stats globales du mois (cours par moniteur, type, etc.)
        stats_mois = DataService.calculer_statistiques_mois(annee, mois)

        # Récupérer tous les cavaliers actifs pour cette période
        date_mois = datetime(annee, mois, 1).date()
        cavaliers_actifs = DataService.get_cavaliers_actifs(at_date=date_mois)

        stats_par_cavalier = {}

        for cavalier in cavaliers_actifs:
            cid = cavalier.get('id')
            stats_par_cavalier[str(cid)] = {
                'cavalier_id': cid,
                'cavalier_name': cavalier.get('name'),
                'email': cavalier.get('email'),
                'phone': cavalier.get('phone'),
                'heures_forfait_co': cavalier.get('heures_forfait_co', 0),
                'heures_cours_part': cavalier.get('heures_cours_part', 0),
                'cours_prevus': 0,  # TODO: compter depuis planning
                'cours_realises': 0,  # TODO: compter depuis planning validé
                'heures_prevues': 0.0,
                'heures_realisees': 0.0,
                'equides_utilises': []  # TODO: extraire depuis planning
            }

        return jsonify({
            'annee': annee,
            'mois': mois,
            'stats_globales': stats_mois,
            'stats_par_cavalier': stats_par_cavalier
        })

    except Exception as e:
        print(f"❌ Erreur get_statistiques_mensuelles_cavalier: {e}")
        return jsonify({'error': 'Erreur lors du calcul des statistiques'}), 500
