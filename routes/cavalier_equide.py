from flask import Blueprint, jsonify, request
from datetime import datetime, date
from typing import Optional, List
from services.data_service import DataService

heures_bp = Blueprint('heures', __name__, url_prefix='/api/heures')


def _validate_date(date_str: str) -> Optional[datetime]:
    """Valider et parser une date ISO (YYYY-MM-DD)"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


def _is_allocation_active(allocation: dict, at_date: Optional[date] = None) -> bool:
    """Vérifier si une allocation est active à une date donnée"""
    if at_date is None:
        at_date = datetime.now().date()

    date_debut = allocation.get('date_debut', '')
    date_fin = allocation.get('date_fin', '')

    # Pas de date de début = actif depuis toujours
    if date_debut:
        debut = _validate_date(date_debut)
        if debut and at_date < debut.date():
            return False

    # Pas de date de fin = actif indéfiniment
    if date_fin:
        fin = _validate_date(date_fin)
        if fin and at_date > fin.date():
            return False

    return True


def _check_overlap(allocations: List[dict], new_debut: date, new_fin: Optional[date], exclude_id: Optional[int] = None) -> Optional[dict]:
    """Vérifier les chevauchements de dates entre allocations"""
    for alloc in allocations:
        # Ignorer l'allocation en cours de modification
        if exclude_id and alloc.get('id') == exclude_id:
            continue

        existing_debut = alloc.get('date_debut', '')
        existing_fin = alloc.get('date_fin', '')

        # Parser les dates existantes
        if existing_debut:
            debut = _validate_date(existing_debut)
            if not debut:
                continue
            existing_debut_date = debut.date()
        else:
            existing_debut_date = date.min  # Depuis toujours

        if existing_fin:
            fin = _validate_date(existing_fin)
            if not fin:
                continue
            existing_fin_date = fin.date()
        else:
            existing_fin_date = date.max  # Jusqu'à la fin des temps

        # Nouvelle période
        new_debut_date = new_debut
        new_fin_date = new_fin if new_fin else date.max

        # Chevauchement si: (start1 <= end2) AND (start2 <= end1)
        if (new_debut_date <= existing_fin_date) and (existing_debut_date <= new_fin_date):
            return alloc

    return None


@heures_bp.route('', methods=['GET'])
def get_all_heures():
    """Récupérer toutes les allocations d'heures"""
    try:
        heures = DataService.read_heures_allocations()

        # Enrichir avec les noms
        cavaliers = DataService.read_cavaliers()
        equides = DataService.read_equides()

        for heure in heures:
            cavalier_id = heure.get('cavalier_id')
            equide_id = heure.get('equide_id')

            cavalier = next((c for c in cavaliers if c.get('id') == cavalier_id), None)
            equide = next((e for e in equides if e.get('id') == equide_id), None)

            heure['cavalier_name'] = cavalier.get('name', 'Inconnu') if cavalier else 'Inconnu'
            heure['equide_name'] = equide.get('name', 'Inconnu') if equide else 'Inconnu'
            heure['equide_type'] = equide.get('type', '') if equide else ''

        return jsonify(heures)
    except Exception as e:
        print(f"❌ Erreur get_all_heures: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des allocations'}), 500


@heures_bp.route('/actives', methods=['GET'])
def get_heures_actives():
    """Récupérer les allocations actives à une date donnée (ou aujourd'hui)"""
    try:
        date_str = request.args.get('date')
        if date_str:
            parsed = _validate_date(date_str)
            if not parsed:
                return jsonify({'error': 'Format de date invalide (YYYY-MM-DD requis)'}), 400
            target_date = parsed.date()
        else:
            target_date = datetime.now().date()

        heures = DataService.read_heures_allocations()
        heures_actives = [h for h in heures if _is_allocation_active(h, target_date)]

        # Enrichir avec les noms
        cavaliers = DataService.read_cavaliers()
        equides = DataService.read_equides()

        for heure in heures_actives:
            cavalier_id = heure.get('cavalier_id')
            equide_id = heure.get('equide_id')

            cavalier = next((c for c in cavaliers if c.get('id') == cavalier_id), None)
            equide = next((e for e in equides if e.get('id') == equide_id), None)

            heure['cavalier_name'] = cavalier.get('name', 'Inconnu') if cavalier else 'Inconnu'
            heure['equide_name'] = equide.get('name', 'Inconnu') if equide else 'Inconnu'
            heure['equide_type'] = equide.get('type', '') if equide else ''

        return jsonify({
            'date': target_date.strftime('%Y-%m-%d'),
            'total': len(heures_actives),
            'allocations': heures_actives
        })
    except Exception as e:
        print(f"❌ Erreur get_heures_actives: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des allocations actives'}), 500


@heures_bp.route('/cavalier/<int:cavalier_id>', methods=['GET'])
def get_heures_cavalier(cavalier_id):
    """Récupérer toutes les allocations d'un cavalier"""
    try:
        heures = DataService.read_heures_allocations()
        heures_cavalier = [h for h in heures if h.get('cavalier_id') == cavalier_id]

        # Enrichir avec les noms des équidés
        equides = DataService.read_equides()
        for heure in heures_cavalier:
            equide_id = heure.get('equide_id')
            equide = next((e for e in equides if e.get('id') == equide_id), None)
            heure['equide_name'] = equide.get('name', 'Inconnu') if equide else 'Inconnu'
            heure['equide_type'] = equide.get('type', '') if equide else ''
            heure['est_actif'] = _is_allocation_active(heure)

        # Calculer le total d'heures actives
        heures_actives = [h for h in heures_cavalier if h['est_actif']]
        total_heures = sum(h.get('hours_per_week', 0) for h in heures_actives)

        return jsonify({
            'cavalier_id': cavalier_id,
            'total_allocations': len(heures_cavalier),
            'allocations_actives': len(heures_actives),
            'total_heures_semaine': total_heures,
            'allocations': heures_cavalier
        })
    except Exception as e:
        print(f"❌ Erreur get_heures_cavalier: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des allocations du cavalier'}), 500


@heures_bp.route('/equide/<int:equide_id>', methods=['GET'])
def get_heures_equide(equide_id):
    """Récupérer toutes les allocations d'un équidé"""
    try:
        heures = DataService.read_heures_allocations()
        heures_equide = [h for h in heures if h.get('equide_id') == equide_id]

        # Enrichir avec les noms des cavaliers
        cavaliers = DataService.read_cavaliers()
        for heure in heures_equide:
            cavalier_id = heure.get('cavalier_id')
            cavalier = next((c for c in cavaliers if c.get('id') == cavalier_id), None)
            heure['cavalier_name'] = cavalier.get('name', 'Inconnu') if cavalier else 'Inconnu'
            heure['est_actif'] = _is_allocation_active(heure)

        # Calculer le total d'heures actives
        heures_actives = [h for h in heures_equide if h['est_actif']]
        total_heures = sum(h.get('hours_per_week', 0) for h in heures_actives)

        return jsonify({
            'equide_id': equide_id,
            'total_allocations': len(heures_equide),
            'allocations_actives': len(heures_actives),
            'total_heures_semaine': total_heures,
            'allocations': heures_equide
        })
    except Exception as e:
        print(f"❌ Erreur get_heures_equide: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des allocations de l\'équidé'}), 500


@heures_bp.route('', methods=['POST'])
def add_allocation():
    """Créer une nouvelle allocation d'heures"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Validation des champs requis
        required_fields = ['cavalier_id', 'equide_id', 'date_debut', 'hours_per_week']
        for field in required_fields:
            if field not in data or (isinstance(data[field], str) and not data[field].strip()):
                return jsonify({'error': f'Le champ "{field}" est requis'}), 400

        cavalier_id = data['cavalier_id']
        equide_id = data['equide_id']
        date_debut_str = data['date_debut'].strip()
        date_fin_str = data.get('date_fin', '').strip()

        # Validation des IDs
        try:
            cavalier_id = int(cavalier_id)
            equide_id = int(equide_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Les IDs doivent être des nombres entiers'}), 400

        # Vérifier que le cavalier existe
        cavaliers = DataService.read_cavaliers()
        if not any(c.get('id') == cavalier_id for c in cavaliers):
            return jsonify({'error': 'Le cavalier spécifié n\'existe pas'}), 404

        # Vérifier que l'équidé existe
        equides = DataService.read_equides()
        if not any(e.get('id') == equide_id for e in equides):
            return jsonify({'error': 'L\'équidé spécifié n\'existe pas'}), 404

        # Validation des dates
        date_debut = _validate_date(date_debut_str)
        if not date_debut:
            return jsonify({'error': 'Format de date de début invalide (YYYY-MM-DD requis)'}), 400

        date_fin = None
        if date_fin_str:
            date_fin = _validate_date(date_fin_str)
            if not date_fin:
                return jsonify({'error': 'Format de date de fin invalide (YYYY-MM-DD requis)'}), 400

            if date_fin.date() <= date_debut.date():
                return jsonify({'error': 'La date de fin doit être après la date de début'}), 400

        # Validation des heures
        try:
            hours_per_week = float(data['hours_per_week'])
            if hours_per_week <= 0 or hours_per_week > 168:  # Max 168h/semaine
                return jsonify({'error': 'Les heures par semaine doivent être entre 0 et 168'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Les heures par semaine doivent être un nombre'}), 400

        heures = DataService.read_heures_allocations()

        # Vérifier les chevauchements pour ce cavalier+équidé
        allocations_existantes = [
            h for h in heures
            if h.get('cavalier_id') == cavalier_id and h.get('equide_id') == equide_id
        ]

        overlap = _check_overlap(allocations_existantes, date_debut.date(), date_fin.date() if date_fin else None)
        if overlap:
            return jsonify({
                'error': 'Cette allocation chevauche une allocation existante',
                'message': f'Conflit avec allocation du {overlap.get("date_debut")} au {overlap.get("date_fin") or "indéfini"}'
            }), 400

        # Générer un nouvel ID
        new_id = max((h.get('id', 0) for h in heures), default=0) + 1

        # Créer la nouvelle allocation
        nouvelle_allocation = {
            'id': new_id,
            'cavalier_id': cavalier_id,
            'equide_id': equide_id,
            'date_debut': date_debut_str,
            'date_fin': date_fin_str,
            'hours_per_week': hours_per_week,
            'notes': data.get('notes', '').strip()
        }
        heures.append(nouvelle_allocation)

        # Sauvegarder
        if not DataService.write_heures_allocations(heures):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        # Enrichir avec les noms pour la réponse
        cavalier = next((c for c in cavaliers if c.get('id') == cavalier_id), None)
        equide = next((e for e in equides if e.get('id') == equide_id), None)
        nouvelle_allocation['cavalier_name'] = cavalier.get('name', '') if cavalier else ''
        nouvelle_allocation['equide_name'] = equide.get('name', '') if equide else ''

        print(f"✅ Allocation créée: Cavalier {cavalier_id} - Équidé {equide_id} - {hours_per_week}h/sem (ID {new_id})")
        return jsonify({'success': True, 'allocation': nouvelle_allocation, 'allocations': heures}), 201

    except Exception as e:
        print(f"❌ Erreur add_allocation: {e}")
        return jsonify({'error': 'Erreur lors de la création de l\'allocation'}), 500


@heures_bp.route('/<int:allocation_id>', methods=['PUT'])
def update_allocation(allocation_id):
    """Mettre à jour une allocation d'heures"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        heures = DataService.read_heures_allocations()

        # Trouver l'allocation
        allocation_index = None
        for i, h in enumerate(heures):
            if h.get('id') == allocation_id:
                allocation_index = i
                break

        if allocation_index is None:
            return jsonify({'error': 'Allocation non trouvée'}), 404

        allocation = heures[allocation_index]

        # Mise à jour des champs avec validation
        if 'cavalier_id' in data:
            cavalier_id = int(data['cavalier_id'])
            cavaliers = DataService.read_cavaliers()
            if not any(c.get('id') == cavalier_id for c in cavaliers):
                return jsonify({'error': 'Le cavalier spécifié n\'existe pas'}), 404
            allocation['cavalier_id'] = cavalier_id

        if 'equide_id' in data:
            equide_id = int(data['equide_id'])
            equides = DataService.read_equides()
            if not any(e.get('id') == equide_id for e in equides):
                return jsonify({'error': 'L\'équidé spécifié n\'existe pas'}), 404
            allocation['equide_id'] = equide_id

        if 'date_debut' in data:
            date_debut_str = data['date_debut'].strip()
            date_debut = _validate_date(date_debut_str)
            if not date_debut:
                return jsonify({'error': 'Format de date de début invalide (YYYY-MM-DD requis)'}), 400
            allocation['date_debut'] = date_debut_str

        if 'date_fin' in data:
            date_fin_str = data['date_fin'].strip() if data['date_fin'] else ''
            if date_fin_str:
                date_fin = _validate_date(date_fin_str)
                if not date_fin:
                    return jsonify({'error': 'Format de date de fin invalide (YYYY-MM-DD requis)'}), 400
            allocation['date_fin'] = date_fin_str

        # Validation cohérence des dates
        debut_str = allocation.get('date_debut', '')
        fin_str = allocation.get('date_fin', '')
        if debut_str and fin_str:
            debut = _validate_date(debut_str)
            fin = _validate_date(fin_str)
            if debut and fin and fin.date() <= debut.date():
                return jsonify({'error': 'La date de fin doit être après la date de début'}), 400

        if 'hours_per_week' in data:
            try:
                hours_per_week = float(data['hours_per_week'])
                if hours_per_week <= 0 or hours_per_week > 168:
                    return jsonify({'error': 'Les heures par semaine doivent être entre 0 et 168'}), 400
                allocation['hours_per_week'] = hours_per_week
            except (ValueError, TypeError):
                return jsonify({'error': 'Les heures par semaine doivent être un nombre'}), 400

        if 'notes' in data:
            allocation['notes'] = data['notes'].strip()

        # Vérifier les chevauchements (en excluant l'allocation actuelle)
        allocations_existantes = [
            h for h in heures
            if h.get('cavalier_id') == allocation['cavalier_id']
               and h.get('equide_id') == allocation['equide_id']
        ]

        debut = _validate_date(allocation['date_debut'])
        fin_str = allocation.get('date_fin', '')
        fin = _validate_date(fin_str) if fin_str else None

        overlap = _check_overlap(
            allocations_existantes,
            debut.date(),
            fin.date() if fin else None,
            exclude_id=allocation_id
        )

        if overlap:
            return jsonify({
                'error': 'Cette allocation chevauche une allocation existante',
                'message': f'Conflit avec allocation du {overlap.get("date_debut")} au {overlap.get("date_fin") or "indéfini"}'
            }), 400

        heures[allocation_index] = allocation

        # Sauvegarder
        if not DataService.write_heures_allocations(heures):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Allocation mise à jour: ID {allocation_id}")
        return jsonify({'success': True, 'allocation': allocation, 'allocations': heures})

    except Exception as e:
        print(f"❌ Erreur update_allocation: {e}")
        return jsonify({'error': 'Erreur lors de la mise à jour de l\'allocation'}), 500


@heures_bp.route('/<int:allocation_id>', methods=['DELETE'])
def delete_allocation(allocation_id):
    """Supprimer une allocation d'heures"""
    try:
        heures = DataService.read_heures_allocations()

        # Trouver et supprimer l'allocation
        allocation_index = None
        for i, h in enumerate(heures):
            if h.get('id') == allocation_id:
                allocation_index = i
                break

        if allocation_index is None:
            return jsonify({'error': 'Allocation non trouvée'}), 404

        deleted = heures.pop(allocation_index)

        # Sauvegarder
        if not DataService.write_heures_allocations(heures):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Allocation supprimée: ID {allocation_id}")
        return jsonify({'success': True, 'deleted': deleted, 'allocations': heures})

    except Exception as e:
        print(f"❌ Erreur delete_allocation: {e}")
        return jsonify({'error': 'Erreur lors de la suppression de l\'allocation'}), 500


@heures_bp.route('/statistiques', methods=['GET'])
def get_statistiques_heures():
    """Obtenir les statistiques sur les allocations d'heures"""
    try:
        heures = DataService.read_heures_allocations()
        cavaliers = DataService.read_cavaliers()
        equides = DataService.read_equides()

        heures_actives = [h for h in heures if _is_allocation_active(h)]

        # Calculs par cavalier
        heures_par_cavalier = {}
        for h in heures_actives:
            cid = h.get('cavalier_id')
            if cid not in heures_par_cavalier:
                heures_par_cavalier[cid] = {
                    'total_heures': 0,
                    'nb_equides': 0,
                    'equides': []
                }
            heures_par_cavalier[cid]['total_heures'] += h.get('hours_per_week', 0)
            heures_par_cavalier[cid]['equides'].append(h.get('equide_id'))

        for cid in heures_par_cavalier:
            heures_par_cavalier[cid]['nb_equides'] = len(set(heures_par_cavalier[cid]['equides']))

        # Calculs par équidé
        heures_par_equide = {}
        for h in heures_actives:
            eid = h.get('equide_id')
            if eid not in heures_par_equide:
                heures_par_equide[eid] = {
                    'total_heures': 0,
                    'nb_cavaliers': 0,
                    'cavaliers': []
                }
            heures_par_equide[eid]['total_heures'] += h.get('hours_per_week', 0)
            heures_par_equide[eid]['cavaliers'].append(h.get('cavalier_id'))

        for eid in heures_par_equide:
            heures_par_equide[eid]['nb_cavaliers'] = len(set(heures_par_equide[eid]['cavaliers']))

        # Top cavaliers
        top_cavaliers = sorted(
            heures_par_cavalier.items(),
            key=lambda x: x[1]['total_heures'],
            reverse=True
        )[:5]

        # Top équidés
        top_equides = sorted(
            heures_par_equide.items(),
            key=lambda x: x[1]['total_heures'],
            reverse=True
        )[:5]

        stats = {
            'total_allocations': len(heures),
            'allocations_actives': len(heures_actives),
            'total_heures_semaine': sum(h.get('hours_per_week', 0) for h in heures_actives),
            'cavaliers_avec_heures': len(heures_par_cavalier),
            'equides_avec_heures': len(heures_par_equide),
            'moyenne_heures_par_cavalier': sum(h.get('hours_per_week', 0) for h in heures_actives) / len(heures_par_cavalier) if heures_par_cavalier else 0,
            'top_cavaliers': [
                {
                    'cavalier_id': cid,
                    'cavalier_name': next((c.get('name', '') for c in cavaliers if c.get('id') == cid), 'Inconnu'),
                    'total_heures': stats['total_heures'],
                    'nb_equides': stats['nb_equides']
                }
                for cid, stats in top_cavaliers
            ],
            'top_equides': [
                {
                    'equide_id': eid,
                    'equide_name': next((e.get('name', '') for e in equides if e.get('id') == eid), 'Inconnu'),
                    'total_heures': stats['total_heures'],
                    'nb_cavaliers': stats['nb_cavaliers']
                }
                for eid, stats in top_equides
            ]
        }

        return jsonify(stats)

    except Exception as e:
        print(f"❌ Erreur get_statistiques_heures: {e}")
        return jsonify({'error': 'Erreur lors du calcul des statistiques'}), 500
