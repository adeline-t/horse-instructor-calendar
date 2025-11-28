from flask import Blueprint, jsonify, request
from services.data_service import DataService

equides_bp = Blueprint('equides', __name__, url_prefix='/api/equides')

# Types d'équidés valides
TYPES_VALIDES = ['Cheval', 'Poney']


def _add_proprietaire_info(equides: list, cavaliers: list) -> list:
    """Ajouter les informations du propriétaire aux équidés"""
    for equide in equides:
        proprietaire_id = equide.get('proprietaire_id')
        if proprietaire_id:
            proprietaire = next((c for c in cavaliers if c.get('id') == proprietaire_id), None)
            equide['proprietaire_name'] = proprietaire.get('name', 'Non trouvé') if proprietaire else 'Non trouvé'
        else:
            equide['proprietaire_name'] = 'Aucun' if not equide.get('owned_by_laury', False) else 'Laury'
    return equides


@equides_bp.route('', methods=['GET'])
def get_equides():
    """Récupérer tous les équidés (masquer les inactifs par défaut)"""
    try:
        masquer_inactifs = request.args.get('masquer_inactifs', 'true').lower() == 'true'

        if masquer_inactifs:
            equides = DataService.get_equides_actifs()
        else:
            equides = DataService.read_equides()

        # Ajouter les informations des propriétaires
        cavaliers = DataService.read_cavaliers()
        equides = _add_proprietaire_info(equides, cavaliers)

        return jsonify(equides)
    except Exception as e:
        print(f"❌ Erreur get_equides: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des équidés'}), 500


@equides_bp.route('/actifs', methods=['GET'])
def get_equides_actifs():
    """Récupérer uniquement les équidés actifs"""
    try:
        equides = DataService.get_equides_actifs()

        # Ajouter les informations des propriétaires
        cavaliers = DataService.read_cavaliers()
        equides = _add_proprietaire_info(equides, cavaliers)

        return jsonify(equides)
    except Exception as e:
        print(f"❌ Erreur get_equides_actifs: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des équidés actifs'}), 500


@equides_bp.route('/disponibles/<int:cavalier_id>', methods=['GET'])
def get_equides_disponibles_pour_cavalier(cavalier_id):
    """Récupérer les équidés disponibles pour un cavalier spécifique"""
    try:
        equides = DataService.get_equides_disponibles_pour_cavalier(cavalier_id)

        # Ajouter les informations des propriétaires
        cavaliers = DataService.read_cavaliers()
        for equide in equides:
            proprietaire_id = equide.get('proprietaire_id')
            if proprietaire_id:
                proprietaire = next((c for c in cavaliers if c.get('id') == proprietaire_id), None)
                equide['proprietaire_name'] = proprietaire.get('name', 'Non trouvé') if proprietaire else 'Non trouvé'
                equide['est_proprietaire'] = proprietaire_id == cavalier_id
            else:
                equide['proprietaire_name'] = 'Laury' if equide.get('owned_by_laury', False) else 'Aucun'
                equide['est_proprietaire'] = False

        return jsonify(equides)
    except Exception as e:
        print(f"❌ Erreur get_equides_disponibles_pour_cavalier: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des équidés disponibles'}), 500


@equides_bp.route('', methods=['POST'])
def add_equide():
    """Ajouter un nouvel équidé"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Validation du nom
        if not data.get('name') or not data['name'].strip():
            return jsonify({'error': 'Le nom de l\'équidé est requis'}), 400

        name = data['name'].strip()
        if len(name) < 2:
            return jsonify({'error': 'Le nom doit contenir au moins 2 caractères'}), 400

        # Validation du type
        type_equide = data.get('type', '').strip()
        if not type_equide or type_equide not in TYPES_VALIDES:
            return jsonify({'error': 'Le type doit être "Cheval" ou "Poney"'}), 400

        equides = DataService.read_equides()

        # Vérifier si l'équidé existe déjà (nom case-insensitive)
        if any(e.get('name', '').lower() == name.lower() for e in equides):
            return jsonify({'error': 'Un équidé avec ce nom existe déjà'}), 400

        # Validation du propriétaire
        proprietaire_id = data.get('proprietaire_id')
        owned_by_laury = data.get('owned_by_laury', False)

        # Logique: si owned_by_laury = True, proprietaire_id doit être None
        if owned_by_laury and proprietaire_id is not None:
            return jsonify({'error': 'Un équidé appartenant à Laury ne peut avoir un autre propriétaire'}), 400

        if proprietaire_id is not None:
            # Vérifier que le propriétaire existe
            cavaliers = DataService.read_cavaliers()
            if not any(c.get('id') == proprietaire_id for c in cavaliers):
                return jsonify({'error': 'Le cavalier propriétaire spécifié n\'existe pas'}), 400

        # Générer un nouvel ID
        new_id = max((e.get('id', 0) for e in equides), default=0) + 1

        # Créer le nouvel équidé
        nouvel_equide = {
            'id': new_id,
            'name': name,
            'type': type_equide,
            'proprietaire_id': proprietaire_id,
            'owned_by_laury': bool(owned_by_laury),
            'actif': data.get('actif', True),
            'notes': data.get('notes', '').strip()
        }
        equides.append(nouvel_equide)

        # Sauvegarder
        if not DataService.write_equides(equides):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Équidé ajouté: {nouvel_equide['name']} ({nouvel_equide['type']}) - ID {new_id}")
        return jsonify({'success': True, 'equide': nouvel_equide, 'equides': equides}), 201

    except Exception as e:
        print(f"❌ Erreur add_equide: {e}")
        return jsonify({'error': 'Erreur lors de l\'ajout de l\'équidé'}), 500


@equides_bp.route('/<int:equide_id>', methods=['PUT'])
def update_equide(equide_id):
    """Mettre à jour un équidé existant"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        equides = DataService.read_equides()

        # Trouver l'équidé
        equide_index = None
        for i, e in enumerate(equides):
            if e.get('id') == equide_id:
                equide_index = i
                break

        if equide_index is None:
            return jsonify({'error': 'Équidé non trouvé'}), 404

        # Mise à jour des champs avec validation
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({'error': 'Le nom doit contenir au moins 2 caractères'}), 400

            # Vérifier que le nouveau nom n'existe pas déjà (sauf pour lui-même)
            for i, e in enumerate(equides):
                if i != equide_index and e.get('name', '').lower() == name.lower():
                    return jsonify({'error': 'Un équidé avec ce nom existe déjà'}), 400

            equides[equide_index]['name'] = name

        if 'type' in data:
            type_equide = data['type'].strip()
            if type_equide not in TYPES_VALIDES:
                return jsonify({'error': 'Le type doit être "Cheval" ou "Poney"'}), 400
            equides[equide_index]['type'] = type_equide

        # Gestion du propriétaire et owned_by_laury
        owned_by_laury = equides[equide_index].get('owned_by_laury', False)
        proprietaire_id = equides[equide_index].get('proprietaire_id')

        if 'owned_by_laury' in data:
            owned_by_laury = bool(data['owned_by_laury'])
            equides[equide_index]['owned_by_laury'] = owned_by_laury

            # Si appartient à Laury, retirer le propriétaire
            if owned_by_laury:
                equides[equide_index]['proprietaire_id'] = None

        if 'proprietaire_id' in data:
            proprietaire_id = data['proprietaire_id']

            # Vérifier la cohérence avec owned_by_laury
            if owned_by_laury and proprietaire_id is not None:
                return jsonify({'error': 'Un équidé appartenant à Laury ne peut avoir un autre propriétaire'}), 400

            if proprietaire_id is not None:
                # Vérifier que le propriétaire existe
                cavaliers = DataService.read_cavaliers()
                if not any(c.get('id') == proprietaire_id for c in cavaliers):
                    return jsonify({'error': 'Le cavalier propriétaire spécifié n\'existe pas'}), 400

            equides[equide_index]['proprietaire_id'] = proprietaire_id

            # Si on assigne un propriétaire, retirer owned_by_laury
            if proprietaire_id is not None:
                equides[equide_index]['owned_by_laury'] = False

        if 'actif' in data:
            equides[equide_index]['actif'] = bool(data['actif'])

        if 'notes' in data:
            equides[equide_index]['notes'] = data['notes'].strip()

        # Sauvegarder
        if not DataService.write_equides(equides):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Équidé mis à jour: {equides[equide_index]['name']} (ID {equide_id})")
        return jsonify({'success': True, 'equide': equides[equide_index], 'equides': equides})

    except Exception as e:
        print(f"❌ Erreur update_equide: {e}")
        return jsonify({'error': 'Erreur lors de la mise à jour de l\'équidé'}), 500


@equides_bp.route('/<int:equide_id>', methods=['DELETE'])
def delete_equide(equide_id):
    """Supprimer un équidé (avec vérification des dépendances)"""
    try:
        # Vérifier les dépendances: heures allouées
        heures = DataService.read_heures_cavaliers()
        for cavalier_id_str, cavalier_heures in heures.items():
            if str(equide_id) in cavalier_heures:
                return jsonify({
                    'error': 'Cet équidé a des heures allouées à des cavaliers',
                    'message': 'Veuillez d\'abord supprimer les heures d\'équitation associées'
                }), 400

        # Vérifier les dépendances: présence dans le planning
        planning = DataService.read_planning()
        has_courses = False
        for semaine in planning.values():
            for jour in semaine.values():
                for creneau in jour.values():
                    for cours in creneau:
                        if equide_id in cours.get('equides', []):
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
                'error': 'Cet équidé est utilisé dans des cours',
                'message': 'Veuillez d\'abord le retirer des cours du planning'
            }), 400

        equides = DataService.read_equides()

        # Trouver et supprimer l'équidé
        equide_index = None
        for i, e in enumerate(equides):
            if e.get('id') == equide_id:
                equide_index = i
                break

        if equide_index is None:
            return jsonify({'error': 'Équidé non trouvé'}), 404

        deleted = equides.pop(equide_index)

        # Sauvegarder
        if not DataService.write_equides(equides):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Équidé supprimé: {deleted.get('name')} (ID {equide_id})")
        return jsonify({'success': True, 'deleted': deleted, 'equides': equides})

    except Exception as e:
        print(f"❌ Erreur delete_equide: {e}")
        return jsonify({'error': 'Erreur lors de la suppression de l\'équidé'}), 500


@equides_bp.route('/<int:equide_id>/proprietaire', methods=['PUT'])
def changer_proprietaire(equide_id):
    """Changer le propriétaire d'un équidé"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        nouveau_proprietaire_id = data.get('proprietaire_id')
        owned_by_laury = data.get('owned_by_laury', False)

        # Validation de la cohérence
        if owned_by_laury and nouveau_proprietaire_id is not None:
            return jsonify({'error': 'Un équidé appartenant à Laury ne peut avoir un autre propriétaire'}), 400

        equides = DataService.read_equides()

        # Trouver l'équidé
        equide_index = None
        for i, e in enumerate(equides):
            if e.get('id') == equide_id:
                equide_index = i
                break

        if equide_index is None:
            return jsonify({'error': 'Équidé non trouvé'}), 404

        # Validation du nouveau propriétaire
        if nouveau_proprietaire_id is not None:
            cavaliers = DataService.read_cavaliers()
            if not any(c.get('id') == nouveau_proprietaire_id for c in cavaliers):
                return jsonify({'error': 'Le cavalier spécifié n\'existe pas'}), 400

        ancien_proprietaire_id = equides[equide_index].get('proprietaire_id')
        ancien_owned_by_laury = equides[equide_index].get('owned_by_laury', False)

        equides[equide_index]['proprietaire_id'] = nouveau_proprietaire_id
        equides[equide_index]['owned_by_laury'] = owned_by_laury

        # Sauvegarder
        if not DataService.write_equides(equides):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Propriétaire changé pour l'équidé {equide_id}: {ancien_proprietaire_id} -> {nouveau_proprietaire_id}, owned_by_laury: {ancien_owned_by_laury} -> {owned_by_laury}")
        return jsonify({
            'success': True,
            'ancien_proprietaire_id': ancien_proprietaire_id,
            'nouveau_proprietaire_id': nouveau_proprietaire_id,
            'owned_by_laury': owned_by_laury
        })

    except Exception as e:
        print(f"❌ Erreur changer_proprietaire: {e}")
        return jsonify({'error': 'Erreur lors du changement de propriétaire'}), 500


@equides_bp.route('/statistiques', methods=['GET'])
def get_statistiques_equides():
    """Obtenir les statistiques détaillées sur les équidés"""
    try:
        equides = DataService.read_equides()
        heures = DataService.read_heures_cavaliers()
        cavaliers = DataService.read_cavaliers()

        stats = {
            'total_equides': len(equides),
            'equides_actifs': len([e for e in equides if e.get('actif', True)]),
            'equides_inactifs': len([e for e in equides if not e.get('actif', True)]),
            'chevaux': len([e for e in equides if e.get('type') == 'Cheval']),
            'poneys': len([e for e in equides if e.get('type') == 'Poney']),
            'avec_proprietaire': len([e for e in equides if e.get('proprietaire_id')]),
            'appartenant_laury': len([e for e in equides if e.get('owned_by_laury', False)]),
            'sans_proprietaire': len([e for e in equides if not e.get('proprietaire_id') and not e.get('owned_by_laury', False)]),
            'total_heures_allouees': 0,
            'equides_plus_utilises': [],
            'details': []
        }

        # Calculer les heures allouées par équidé
        heures_par_equide = {}
        cavaliers_par_equide = {}

        for cavalier_id_str, cavalier_heures in heures.items():
            for equide_id_str, heures_semaine in cavalier_heures.items():
                equide_id_int = int(equide_id_str)

                if equide_id_int not in heures_par_equide:
                    heures_par_equide[equide_id_int] = 0
                    cavaliers_par_equide[equide_id_int] = []

                heures_par_equide[equide_id_int] += heures_semaine
                cavaliers_par_equide[equide_id_int].append(int(cavalier_id_str))
                stats['total_heures_allouees'] += heures_semaine

        # Trier les équidés les plus utilisés
        equides_tries = sorted(heures_par_equide.items(), key=lambda x: x[1], reverse=True)[:5]
        stats['equides_plus_utilises'] = [
            {
                'equide_id': equide_id,
                'nom': next((e.get('name', '') for e in equides if e.get('id') == equide_id), 'Inconnu'),
                'heures': heures,
                'nb_cavaliers': len(set(cavaliers_par_equide.get(equide_id, [])))
            }
            for equide_id, heures in equides_tries
        ]

        # Détails par équidé
        for equide in equides:
            equide_id = equide['id']
            heures_allouees = heures_par_equide.get(equide_id, 0)
            cavaliers_utilisant = list(set(cavaliers_par_equide.get(equide_id, [])))

            proprietaire_id = equide.get('proprietaire_id')
            proprietaire_name = ''
            if proprietaire_id:
                proprietaire = next((c for c in cavaliers if c.get('id') == proprietaire_id), None)
                proprietaire_name = proprietaire.get('name', 'Non trouvé') if proprietaire else 'Non trouvé'
            elif equide.get('owned_by_laury', False):
                proprietaire_name = 'Laury'

            stats['details'].append({
                'id': equide_id,
                'name': equide['name'],
                'type': equide['type'],
                'actif': equide.get('actif', True),
                'proprietaire_id': proprietaire_id,
                'proprietaire_name': proprietaire_name,
                'owned_by_laury': equide.get('owned_by_laury', False),
                'heures_allouees': heures_allouees,
                'nb_cavaliers': len(cavaliers_utilisant),
                'cavaliers_ids': cavaliers_utilisant,
                'notes': equide.get('notes', '')
            })

        # Trier les détails par nombre d'heures décroissant
        stats['details'].sort(key=lambda x: x['heures_allouees'], reverse=True)

        return jsonify(stats)

    except Exception as e:
        print(f"❌ Erreur get_statistiques_equides: {e}")
        return jsonify({'error': 'Erreur lors du calcul des statistiques'}), 500


@equides_bp.route('/types', methods=['GET'])
def get_types_valides():
    """Récupérer la liste des types d'équidés valides"""
    return jsonify({
        'types': TYPES_VALIDES
    })
