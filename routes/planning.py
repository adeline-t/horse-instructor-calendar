from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, date, time
from typing import Optional, List, Dict, Tuple
from services.data_service import DataService

planning_bp = Blueprint('planning', __name__, url_prefix='/api/planning')

# Jours de la semaine en français
JOURS_SEMAINE = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']


def _get_week_start(target_date: date) -> date:
    """Obtenir le lundi de la semaine contenant la date"""
    return target_date - timedelta(days=target_date.weekday())


def _get_jour_name(target_date: date) -> str:
    """Obtenir le nom du jour en français"""
    return JOURS_SEMAINE[target_date.weekday()]


def _parse_time(time_str: str) -> Optional[time]:
    """Parser une heure au format HH:MM"""
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return None


def _time_to_minutes(t: time) -> int:
    """Convertir un objet time en minutes depuis minuit"""
    return t.hour * 60 + t.minute


def _get_session_key(date_str: str, heure_debut: str) -> str:
    """Créer une clé unique pour une session"""
    return f"{date_str}|{heure_debut}"


def _parse_session_key(session_key: str) -> Tuple[str, str]:
    """Parser une clé de session"""
    parts = session_key.split('|', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    # Fallback pour ancien format
    return session_key.split('_', 1)


def _check_time_overlap(existing_sessions: List[dict], new_heure_debut: time, new_duree: int, exclude_key: Optional[str] = None) -> Optional[dict]:
    """Vérifier les chevauchements horaires entre sessions"""
    new_debut_minutes = _time_to_minutes(new_heure_debut)
    new_fin_minutes = new_debut_minutes + new_duree

    for session in existing_sessions:
        session_key = session.get('key')

        # Ignorer la session en cours de modification
        if exclude_key and session_key == exclude_key:
            continue

        try:
            session_heure_debut = _parse_time(session.get('heure_debut', ''))
            if not session_heure_debut:
                continue

            session_debut_minutes = _time_to_minutes(session_heure_debut)
            session_fin_minutes = session_debut_minutes + session.get('duree_minutes', 60)

            # Chevauchement si: (start1 < end2) AND (start2 < end1)
            if (new_debut_minutes < session_fin_minutes) and (session_debut_minutes < new_fin_minutes):
                return session
        except:
            continue

    return None


def _get_allocated_equides_for_cavalier(cavalier_id: int, session_date: date) -> List[int]:
    """Récupérer les équidés alloués à un cavalier pour une date donnée"""
    heures = DataService.read_heures_allocations()
    equides_ids = []

    for allocation in heures:
        if allocation.get('cavalier_id') != cavalier_id:
            continue

        # Vérifier si l'allocation est active à cette date
        date_debut_str = allocation.get('date_debut', '')
        date_fin_str = allocation.get('date_fin', '')

        is_active = True

        if date_debut_str:
            try:
                date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
                if session_date < date_debut:
                    is_active = False
            except ValueError:
                continue

        if date_fin_str:
            try:
                date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
                if session_date > date_fin:
                    is_active = False
            except ValueError:
                continue

        if is_active:
            equide_id = allocation.get('equide_id')
            if equide_id and equide_id not in equides_ids:
                equides_ids.append(equide_id)

    return equides_ids


def _auto_add_equides(cavaliers_ids: List[int], session_date: date) -> List[int]:
    """Ajouter automatiquement les équidés alloués aux cavaliers"""
    equides_ids = []

    for cavalier_id in cavaliers_ids:
        allocated = _get_allocated_equides_for_cavalier(cavalier_id, session_date)
        for equide_id in allocated:
            if equide_id not in equides_ids:
                equides_ids.append(equide_id)

    return equides_ids


def _validate_disponibilite(jour: str, heure_debut: time, duree_minutes: int) -> Tuple[bool, Optional[str]]:
    """Vérifier qu'une session est dans les disponibilités"""
    disponibilites = DataService.read_disponibilites()
    jour_dispos = disponibilites.get(jour, [])

    if not jour_dispos:
        return False, f"Aucune disponibilité pour {jour}"

    debut_minutes = _time_to_minutes(heure_debut)
    fin_minutes = debut_minutes + duree_minutes

    # Vérifier si la session est dans au moins un créneau de disponibilité
    for dispo in jour_dispos:
        try:
            dispo_debut = _parse_time(dispo.get('debut', ''))
            dispo_fin = _parse_time(dispo.get('fin', ''))

            if not dispo_debut or not dispo_fin:
                continue

            dispo_debut_minutes = _time_to_minutes(dispo_debut)
            dispo_fin_minutes = _time_to_minutes(dispo_fin)

            # La session doit être entièrement dans le créneau
            if debut_minutes >= dispo_debut_minutes and fin_minutes <= dispo_fin_minutes:
                return True, None
        except:
            continue

    return False, f"La session ({heure_debut.strftime('%H:%M')} - {duree_minutes}min) n'est pas dans les disponibilités de {jour}"


@planning_bp.route('/week', methods=['GET'])
def get_week_planning():
    """Récupérer le planning pour une semaine donnée"""
    try:
        week_start_str = request.args.get('week_start')

        if not week_start_str:
            today = datetime.now().date()
            week_start = _get_week_start(today)
        else:
            try:
                week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
                week_start = _get_week_start(week_start)
            except ValueError:
                return jsonify({'error': 'Format de date invalide (YYYY-MM-DD requis)'}), 400

        # Récupérer le planning brut
        planning_raw = DataService.get_semaine_planning(week_start)

        # Organiser par jour
        planning_structure = {}
        for i in range(7):
            jour_date = week_start + timedelta(days=i)
            jour_name = _get_jour_name(jour_date)
            jour_date_str = jour_date.strftime('%Y-%m-%d')

            planning_structure[jour_name] = {
                'date': jour_date_str,
                'sessions': []
            }

        # Remplir avec les sessions existantes
        for session_key, session_data in planning_raw.items():
            date_str, heure_debut = _parse_session_key(session_key)

            try:
                session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                jour_name = _get_jour_name(session_date)

                if jour_name in planning_structure:
                    session_with_key = session_data.copy()
                    session_with_key['key'] = session_key
                    planning_structure[jour_name]['sessions'].append(session_with_key)
            except ValueError:
                print(f"⚠️ Session ignorée (date invalide): {session_key}")
                continue

        # Trier les sessions par heure de début
        for jour in planning_structure.values():
            jour['sessions'].sort(key=lambda s: s.get('heure_debut', ''))

        # Ajouter les données de référence
        cavaliers = DataService.read_cavaliers()
        equides = DataService.read_equides()
        disponibilites = DataService.read_disponibilites()
        cours_recurrents = DataService.read_cours_recurrents()

        # Filtrer uniquement les actifs
        cavaliers_actifs = [c for c in cavaliers if c.get('actif', True)]
        equides_actifs = [e for e in equides if e.get('actif', True)]

        return jsonify({
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': (week_start + timedelta(days=6)).strftime('%Y-%m-%d'),
            'planning': planning_structure,
            'cavaliers': cavaliers_actifs,
            'equides': equides_actifs,
            'disponibilites': disponibilites,
            'cours_recurrents': cours_recurrents
        })
    except Exception as e:
        print(f"❌ Erreur get_week_planning: {e}")
        return jsonify({'error': 'Erreur lors de la récupération du planning'}), 500


@planning_bp.route('/session', methods=['POST'])
def save_session():
    """Sauvegarder ou mettre à jour une séance de cours"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Extraction des données
        date_str = data.get('date', '').strip()
        heure_debut_str = data.get('heure_debut', '').strip()
        duree_minutes = data.get('duree_minutes')
        cavaliers_ids = data.get('cavaliers', [])
        equides_ids = data.get('equides', [])  # Optionnel, sera auto-complété
        instructor = data.get('instructor', '').strip()
        notes = data.get('notes', '').strip()
        type_cours = data.get('type_cours', 'cours')
        cours_recurrent_id = data.get('cours_recurrent_id')  # Si créé depuis un cours récurrent

        # Validation basique
        if not date_str:
            return jsonify({'error': 'La date est requise'}), 400

        if not heure_debut_str:
            return jsonify({'error': 'L\'heure de début est requise'}), 400

        if not duree_minutes or not isinstance(duree_minutes, (int, float)):
            return jsonify({'error': 'La durée en minutes est requise'}), 400

        if duree_minutes <= 0 or duree_minutes > 480:  # Max 8h
            return jsonify({'error': 'La durée doit être entre 1 et 480 minutes'}), 400

        # Validation de la date
        try:
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide (YYYY-MM-DD requis)'}), 400

        # Validation de l'heure
        heure_debut = _parse_time(heure_debut_str)
        if not heure_debut:
            return jsonify({'error': 'Format d\'heure invalide (HH:MM requis)'}), 400

        # Vérifier que c'est dans les disponibilités
        jour_name = _get_jour_name(session_date)
        is_valid, error_msg = _validate_disponibilite(jour_name, heure_debut, duree_minutes)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Validation des IDs
        if not isinstance(cavaliers_ids, list):
            return jsonify({'error': 'Les cavaliers doivent être une liste'}), 400

        if not isinstance(equides_ids, list):
            return jsonify({'error': 'Les équidés doivent être une liste'}), 400

        # Vérifier qu'il y a au moins un cavalier
        if len(cavaliers_ids) == 0:
            return jsonify({'error': 'Il faut au moins un cavalier'}), 400

        # Vérifier que les cavaliers existent
        all_cavaliers = DataService.read_cavaliers()
        for cid in cavaliers_ids:
            if not any(c.get('id') == cid for c in all_cavaliers):
                return jsonify({'error': f'Le cavalier ID {cid} n\'existe pas'}), 404

        # Auto-ajouter les équidés alloués aux cavaliers
        auto_equides = _auto_add_equides(cavaliers_ids, session_date)

        # Fusionner avec les équidés manuellement ajoutés
        all_equides_ids = list(set(equides_ids + auto_equides))

        # Vérifier que les équidés existent
        all_equides = DataService.read_equides()
        for eid in all_equides_ids:
            if not any(e.get('id') == eid for e in all_equides):
                return jsonify({'error': f'L\'équidé ID {eid} n\'existe pas'}), 404

        # Récupérer le planning de la semaine
        week_start = _get_week_start(session_date)
        planning = DataService.get_semaine_planning(week_start)

        # Créer la clé pour cette séance
        session_key = _get_session_key(date_str, heure_debut_str)

        # Vérifier les chevauchements horaires (cavaliers et équidés)
        sessions_du_jour = []
        for key, session in planning.items():
            s_date, _ = _parse_session_key(key)
            if s_date == date_str:
                session_copy = session.copy()
                session_copy['key'] = key
                sessions_du_jour.append(session_copy)

        overlap = _check_time_overlap(sessions_du_jour, heure_debut, duree_minutes, exclude_key=session_key)

        if overlap:
            # Vérifier s'il y a des conflits de cavaliers ou équidés
            overlap_cavaliers = set(overlap.get('cavaliers', []))
            overlap_equides = set(overlap.get('equides', []))

            conflict_cavaliers = overlap_cavaliers.intersection(set(cavaliers_ids))
            conflict_equides = overlap_equides.intersection(set(all_equides_ids))

            if conflict_cavaliers or conflict_equides:
                error_parts = []
                if conflict_cavaliers:
                    cavalier_names = [c.get('name') for c in all_cavaliers if c.get('id') in conflict_cavaliers]
                    error_parts.append(f"Cavaliers: {', '.join(cavalier_names)}")
                if conflict_equides:
                    equide_names = [e.get('name') for e in all_equides if e.get('id') in conflict_equides]
                    error_parts.append(f"Équidés: {', '.join(equide_names)}")

                return jsonify({
                    'error': 'Conflit horaire détecté',
                    'message': f"{' | '.join(error_parts)} déjà occupé(s) entre {overlap.get('heure_debut')} et {overlap.get('heure_fin')}"
                }), 400

        # Calculer l'heure de fin
        debut_dt = datetime.combine(session_date, heure_debut)
        fin_dt = debut_dt + timedelta(minutes=duree_minutes)
        heure_fin_str = fin_dt.strftime('%H:%M')

        # Enrichir avec les noms pour faciliter l'affichage
        cavaliers_names = [c.get('name', '') for c in all_cavaliers if c.get('id') in cavaliers_ids]
        equides_names = [e.get('name', '') for e in all_equides if e.get('id') in all_equides_ids]

        # Créer ou mettre à jour la séance
        session_data = {
            'date': date_str,
            'jour': jour_name,
            'heure_debut': heure_debut_str,
            'heure_fin': heure_fin_str,
            'duree_minutes': duree_minutes,
            'cavaliers': cavaliers_ids,
            'cavaliers_names': cavaliers_names,
            'equides': all_equides_ids,
            'equides_names': equides_names,
            'equides_auto_added': auto_equides,  # Pour tracer les équidés ajoutés automatiquement
            'instructor': instructor,
            'notes': notes,
            'type_cours': type_cours,
            'cours_recurrent_id': cours_recurrent_id,
            'updated_at': datetime.now().isoformat()
        }

        # Ajouter created_at si nouvelle session
        if session_key not in planning:
            session_data['created_at'] = datetime.now().isoformat()
        else:
            session_data['created_at'] = planning[session_key].get('created_at', datetime.now().isoformat())

        planning[session_key] = session_data

        # Sauvegarder le planning
        if not DataService.save_semaine_planning(week_start, planning):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Session sauvegardée: {date_str} {heure_debut_str}-{heure_fin_str} - {len(cavaliers_ids)} cavaliers, {len(all_equides_ids)} équidés")

        session_data['key'] = session_key

        return jsonify({
            'success': True,
            'session': session_data,
            'session_key': session_key,
            'auto_added_equides_count': len(auto_equides)
        }), 201

    except Exception as e:
        print(f"❌ Erreur save_session: {e}")
        return jsonify({'error': 'Erreur lors de la sauvegarde de la session'}), 500


@planning_bp.route('/session/from-recurrent', methods=['POST'])
def create_session_from_recurrent():
    """Créer une session à partir d'un cours récurrent"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        cours_recurrent_id = data.get('cours_recurrent_id')
        date_str = data.get('date', '').strip()

        if not cours_recurrent_id:
            return jsonify({'error': 'L\'ID du cours récurrent est requis'}), 400

        if not date_str:
            return jsonify({'error': 'La date est requise'}), 400

        # Validation de la date
        try:
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide (YYYY-MM-DD requis)'}), 400

        # Récupérer le cours récurrent
        cours_recurrents = DataService.read_cours_recurrents()
        cours_recurrent = next((c for c in cours_recurrents if c.get('id') == cours_recurrent_id), None)

        if not cours_recurrent:
            return jsonify({'error': 'Cours récurrent non trouvé'}), 404

        # Vérifier que le jour correspond
        jour_name = _get_jour_name(session_date)
        if cours_recurrent.get('jour') != jour_name:
            return jsonify({'error': f'Le cours récurrent est pour {cours_recurrent.get("jour")}, pas {jour_name}'}), 400

        # Extraire les données du cours récurrent
        heure_debut_str = cours_recurrent.get('heure_debut', '')
        duree_minutes = cours_recurrent.get('duree_minutes', 60)
        cavaliers_ids = cours_recurrent.get('cavaliers', [])
        instructor = cours_recurrent.get('instructor', '')
        notes = cours_recurrent.get('notes', '')
        type_cours = cours_recurrent.get('type_cours', 'cours')

        # Créer la session via l'endpoint de sauvegarde
        session_data_request = {
            'date': date_str,
            'heure_debut': heure_debut_str,
            'duree_minutes': duree_minutes,
            'cavaliers': cavaliers_ids,
            'equides': [],  # Seront auto-ajoutés
            'instructor': instructor,
            'notes': notes,
            'type_cours': type_cours,
            'cours_recurrent_id': cours_recurrent_id
        }

        # Réutiliser la logique de save_session
        # (On pourrait aussi appeler directement save_session, mais ici on duplique pour plus de contrôle)

        heure_debut = _parse_time(heure_debut_str)
        if not heure_debut:
            return jsonify({'error': 'Heure de début invalide dans le cours récurrent'}), 400

        # Vérifier disponibilité
        is_valid, error_msg = _validate_disponibilite(jour_name, heure_debut, duree_minutes)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Auto-ajouter les équidés
        all_cavaliers = DataService.read_cavaliers()
        for cid in cavaliers_ids:
            if not any(c.get('id') == cid for c in all_cavaliers):
                return jsonify({'error': f'Le cavalier ID {cid} du cours récurrent n\'existe plus'}), 404

        auto_equides = _auto_add_equides(cavaliers_ids, session_date)

        # Vérifier équidés
        all_equides = DataService.read_equides()
        for eid in auto_equides:
            if not any(e.get('id') == eid for e in all_equides):
                return jsonify({'error': f'L\'équidé ID {eid} n\'existe plus'}), 404

        # Récupérer le planning
        week_start = _get_week_start(session_date)
        planning = DataService.get_semaine_planning(week_start)

        session_key = _get_session_key(date_str, heure_debut_str)

        # Vérifier si la session existe déjà
        if session_key in planning:
            return jsonify({'error': 'Une session existe déjà à cet horaire'}), 400

        # Vérifier chevauchements
        sessions_du_jour = []
        for key, session in planning.items():
            s_date, _ = _parse_session_key(key)
            if s_date == date_str:
                session_copy = session.copy()
                session_copy['key'] = key
                sessions_du_jour.append(session_copy)

        overlap = _check_time_overlap(sessions_du_jour, heure_debut, duree_minutes)
        if overlap:
            overlap_cavaliers = set(overlap.get('cavaliers', []))
            overlap_equides = set(overlap.get('equides', []))

            conflict_cavaliers = overlap_cavaliers.intersection(set(cavaliers_ids))
            conflict_equides = overlap_equides.intersection(set(auto_equides))

            if conflict_cavaliers or conflict_equides:
                return jsonify({
                    'error': 'Conflit horaire avec une session existante',
                    'message': 'Des cavaliers ou équidés sont déjà occupés à cet horaire'
                }), 400

        # Calculer heure de fin
        debut_dt = datetime.combine(session_date, heure_debut)
        fin_dt = debut_dt + timedelta(minutes=duree_minutes)
        heure_fin_str = fin_dt.strftime('%H:%M')

        # Enrichir avec noms
        cavaliers_names = [c.get('name', '') for c in all_cavaliers if c.get('id') in cavaliers_ids]
        equides_names = [e.get('name', '') for e in all_equides if e.get('id') in auto_equides]

        # Créer la session
        session_data = {
            'date': date_str,
            'jour': jour_name,
            'heure_debut': heure_debut_str,
            'heure_fin': heure_fin_str,
            'duree_minutes': duree_minutes,
            'cavaliers': cavaliers_ids,
            'cavaliers_names': cavaliers_names,
            'equides': auto_equides,
            'equides_names': equides_names,
            'equides_auto_added': auto_equides,
            'instructor': instructor,
            'notes': notes,
            'type_cours': type_cours,
            'cours_recurrent_id': cours_recurrent_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        planning[session_key] = session_data

        # Sauvegarder
        if not DataService.save_semaine_planning(week_start, planning):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Session créée depuis cours récurrent {cours_recurrent_id}: {date_str} {heure_debut_str}")

        session_data['key'] = session_key

        return jsonify({
            'success': True,
            'session': session_data,
            'session_key': session_key,
            'cours_recurrent_id': cours_recurrent_id
        }), 201

    except Exception as e:
        print(f"❌ Erreur create_session_from_recurrent: {e}")
        return jsonify({'error': 'Erreur lors de la création depuis le cours récurrent'}), 500


@planning_bp.route('/session', methods=['DELETE'])
def delete_session():
    """Supprimer une séance de cours"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        date_str = data.get('date', '').strip()
        heure_debut_str = data.get('heure_debut', '').strip()

        if not date_str or not heure_debut_str:
            return jsonify({'error': 'Date et heure de début requises'}), 400

        # Validation de la date
        try:
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400

        # Récupérer le planning
        week_start = _get_week_start(session_date)
        planning = DataService.get_semaine_planning(week_start)

        session_key = _get_session_key(date_str, heure_debut_str)

        # Supprimer la session
        if session_key in planning:
            deleted_session = planning.pop(session_key)

            # Sauvegarder
            if not DataService.save_semaine_planning(week_start, planning):
                return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

            print(f"✅ Session supprimée: {session_key}")
            return jsonify({
                'success': True,
                'deleted': deleted_session
            })
        else:
            return jsonify({'error': 'Session non trouvée'}), 404

    except Exception as e:
        print(f"❌ Erreur delete_session: {e}")
        return jsonify({'error': 'Erreur lors de la suppression de la session'}), 500


@planning_bp.route('/availability', methods=['GET'])
def check_availability():
    """Vérifier la disponibilité des cavaliers et équidés pour un créneau horaire"""
    try:
        date_str = request.args.get('date', '').strip()
        heure_debut_str = request.args.get('heure_debut', '').strip()
        duree_minutes = request.args.get('duree_minutes', type=int)
        exclude_session = request.args.get('exclude_session') == 'true'

        if not date_str or not heure_debut_str or not duree_minutes:
            return jsonify({'error': 'Date, heure de début et durée requis'}), 400

        # Validation
        try:
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400

        heure_debut = _parse_time(heure_debut_str)
        if not heure_debut:
            return jsonify({'error': 'Format d\'heure invalide'}), 400

        week_start = _get_week_start(session_date)
        planning = DataService.get_semaine_planning(week_start)

        session_key = _get_session_key(date_str, heure_debut_str)

        # Trouver les sessions qui se chevauchent
        occupied_cavaliers = set()
        occupied_equides = set()

        sessions_du_jour = []
        for key, session in planning.items():
            s_date, _ = _parse_session_key(key)
            if s_date == date_str:
                session_copy = session.copy()
                session_copy['key'] = key
                sessions_du_jour.append(session_copy)

        for session in sessions_du_jour:
            if exclude_session and session.get('key') == session_key:
                continue

            # Vérifier chevauchement horaire
            try:
                session_heure_debut = _parse_time(session.get('heure_debut', ''))
                if not session_heure_debut:
                    continue

                session_debut_minutes = _time_to_minutes(session_heure_debut)
                session_fin_minutes = session_debut_minutes + session.get('duree_minutes', 60)

                debut_minutes = _time_to_minutes(heure_debut)
                fin_minutes = debut_minutes + duree_minutes

                # Si chevauchement horaire
                if (debut_minutes < session_fin_minutes) and (session_debut_minutes < fin_minutes):
                    occupied_cavaliers.update(session.get('cavaliers', []))
                    occupied_equides.update(session.get('equides', []))
            except:
                continue

        # Récupérer tous les cavaliers et équidés actifs
        all_cavaliers = DataService.read_cavaliers()
        all_equides = DataService.read_equides()

        available_cavaliers = [
            c for c in all_cavaliers
            if c.get('actif', True) and c.get('id') not in occupied_cavaliers
        ]

        available_equides = [
            e for e in all_equides
            if e.get('actif', True) and e.get('id') not in occupied_equides
        ]

        # Enrichir les cavaliers avec leurs équidés alloués
        for cavalier in available_cavaliers:
            allocated = _get_allocated_equides_for_cavalier(cavalier.get('id'), session_date)
            # Filtrer les équidés alloués qui sont aussi disponibles
            available_allocated = [eid for eid in allocated if eid not in occupied_equides]
            cavalier['allocated_equides'] = available_allocated

            # Ajouter les noms des équidés alloués
            equides_names = [e.get('name', '') for e in all_equides if e.get('id') in available_allocated]
            cavalier['allocated_equides_names'] = equides_names

        return jsonify({
            'date': date_str,
            'heure_debut': heure_debut_str,
            'duree_minutes': duree_minutes,
            'occupied': {
                'cavaliers': list(occupied_cavaliers),
                'equides': list(occupied_equides)
            },
            'available': {
                'cavaliers': available_cavaliers,
                'equides': available_equides
            }
        })

    except Exception as e:
        print(f"❌ Erreur check_availability: {e}")
        return jsonify({'error': 'Erreur lors de la vérification de disponibilité'}), 500


@planning_bp.route('/generate-from-recurrent', methods=['POST'])
def generate_from_recurrent():
    """Générer automatiquement toutes les sessions d'une semaine depuis les cours récurrents"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        week_start_str = data.get('week_start', '').strip()
        overwrite = data.get('overwrite', False)  # Écraser les sessions existantes?

        if not week_start_str:
            return jsonify({'error': 'La date de début de semaine est requise'}), 400

        # Validation
        try:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
            week_start = _get_week_start(week_start)
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400

        # Récupérer les cours récurrents
        cours_recurrents = DataService.read_cours_recurrents()

        if not cours_recurrents:
            return jsonify({'error': 'Aucun cours récurrent défini'}), 400

        # Récupérer le planning existant
        planning = DataService.get_semaine_planning(week_start)

        created_count = 0
        skipped_count = 0
        errors = []

        # Pour chaque jour de la semaine
        for i in range(7):
            jour_date = week_start + timedelta(days=i)
            jour_name = _get_jour_name(jour_date)
            date_str = jour_date.strftime('%Y-%m-%d')

            # Trouver les cours récurrents pour ce jour
            cours_du_jour = [c for c in cours_recurrents if c.get('jour') == jour_name and c.get('actif', True)]

            for cours in cours_du_jour:
                try:
                    heure_debut_str = cours.get('heure_debut', '')
                    session_key = _get_session_key(date_str, heure_debut_str)

                    # Vérifier si la session existe déjà
                    if session_key in planning and not overwrite:
                        skipped_count += 1
                        continue

                    # Extraire les données
                    heure_debut = _parse_time(heure_debut_str)
                    if not heure_debut:
                        errors.append(f"Heure invalide pour cours {cours.get('id')} le {jour_name}")
                        continue

                    duree_minutes = cours.get('duree_minutes', 60)
                    cavaliers_ids = cours.get('cavaliers', [])
                    instructor = cours.get('instructor', '')
                    notes = cours.get('notes', '')
                    type_cours = cours.get('type_cours', 'cours')

                    # Vérifier disponibilité
                    is_valid, error_msg = _validate_disponibilite(jour_name, heure_debut, duree_minutes)
                    if not is_valid:
                        errors.append(f"Cours {cours.get('id')} le {jour_name}: {error_msg}")
                        continue

                    # Auto-ajouter équidés
                    all_cavaliers = DataService.read_cavaliers()
                    all_equides = DataService.read_equides()

                    # Valider cavaliers
                    valid_cavaliers = []
                    for cid in cavaliers_ids:
                        if any(c.get('id') == cid for c in all_cavaliers):
                            valid_cavaliers.append(cid)
                        else:
                            errors.append(f"Cavalier {cid} du cours {cours.get('id')} n'existe plus")

                    if not valid_cavaliers:
                        errors.append(f"Aucun cavalier valide pour cours {cours.get('id')} le {jour_name}")
                        continue

                    auto_equides = _auto_add_equides(valid_cavaliers, jour_date)

                    # Valider équidés
                    valid_equides = [eid for eid in auto_equides if any(e.get('id') == eid for e in all_equides)]

                    # Calculer heure de fin
                    debut_dt = datetime.combine(jour_date, heure_debut)
                    fin_dt = debut_dt + timedelta(minutes=duree_minutes)
                    heure_fin_str = fin_dt.strftime('%H:%M')

                    # Enrichir avec noms
                    cavaliers_names = [c.get('name', '') for c in all_cavaliers if c.get('id') in valid_cavaliers]
                    equides_names = [e.get('name', '') for e in all_equides if e.get('id') in valid_equides]

                    # Créer la session
                    session_data = {
                        'date': date_str,
                        'jour': jour_name,
                        'heure_debut': heure_debut_str,
                        'heure_fin': heure_fin_str,
                        'duree_minutes': duree_minutes,
                        'cavaliers': valid_cavaliers,
                        'cavaliers_names': cavaliers_names,
                        'equides': valid_equides,
                        'equides_names': equides_names,
                        'equides_auto_added': valid_equides,
                        'instructor': instructor,
                        'notes': notes,
                        'type_cours': type_cours,
                        'cours_recurrent_id': cours.get('id'),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'auto_generated': True
                    }

                    planning[session_key] = session_data
                    created_count += 1

                except Exception as e:
                    errors.append(f"Erreur cours {cours.get('id')} le {jour_name}: {str(e)}")
                    continue

        # Sauvegarder le planning
        if not DataService.save_semaine_planning(week_start, planning):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Génération automatique: {created_count} sessions créées, {skipped_count} ignorées")

        response = {
            'success': True,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'total_sessions': len(planning),
            'week_start': week_start.strftime('%Y-%m-%d')
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 201

    except Exception as e:
        print(f"❌ Erreur generate_from_recurrent: {e}")
        return jsonify({'error': 'Erreur lors de la génération automatique'}), 500


@planning_bp.route('/copy', methods=['POST'])
def copy_week():
    """Copier le planning d'une semaine à une autre"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        from_week_str = data.get('from_week', '').strip()
        to_week_str = data.get('to_week', '').strip()
        overwrite = data.get('overwrite', False)

        if not from_week_str or not to_week_str:
            return jsonify({'error': 'Semaines source et destination requises'}), 400

        # Validation des dates
        try:
            from_date = datetime.strptime(from_week_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_week_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400

        from_week = _get_week_start(from_date)
        to_week = _get_week_start(to_date)

        if from_week == to_week:
            return jsonify({'error': 'Les semaines source et destination sont identiques'}), 400

        # Récupérer le planning source
        source_planning = DataService.get_semaine_planning(from_week)

        if not source_planning:
            return jsonify({'error': 'Aucune session à copier dans la semaine source'}), 400

        # Récupérer le planning destination
        dest_planning = DataService.get_semaine_planning(to_week) if not overwrite else {}

        # Calculer le décalage
        day_offset = (to_week - from_week).days

        copied_count = 0
        skipped_count = 0
        errors = []

        for session_key, session_data in source_planning.items():
            try:
                date_str, heure_debut = _parse_session_key(session_key)
                old_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                new_date = old_date + timedelta(days=day_offset)
                new_date_str = new_date.strftime('%Y-%m-%d')
                new_jour = _get_jour_name(new_date)

                new_session_key = _get_session_key(new_date_str, heure_debut)

                # Vérifier si existe déjà
                if not overwrite and new_session_key in dest_planning:
                    skipped_count += 1
                    continue

                # Copier les données
                new_session_data = {
                    'date': new_date_str,
                    'jour': new_jour,
                    'heure_debut': session_data.get('heure_debut', ''),
                    'heure_fin': session_data.get('heure_fin', ''),
                    'duree_minutes': session_data.get('duree_minutes', 60),
                    'cavaliers': session_data.get('cavaliers', []).copy() if isinstance(
                        session_data.get('cavaliers', []), list) else [],
                    'cavaliers_names': session_data.get('cavaliers_names', []).copy() if isinstance(
                        session_data.get('cavaliers_names', []), list) else [],
                    'equides': session_data.get('equides', []).copy() if isinstance(session_data.get('equides', []),
                                                                                    list) else [],
                    'equides_names': session_data.get('equides_names', []).copy() if isinstance(
                        session_data.get('equides_names', []), list) else [],
                    'equides_auto_added': session_data.get('equides_auto_added', []).copy() if isinstance(
                        session_data.get('equides_auto_added', []), list) else [],
                    'instructor': session_data.get('instructor', ''),
                    'notes': session_data.get('notes', ''),
                    'type_cours': session_data.get('type_cours', 'cours'),
                    'cours_recurrent_id': session_data.get('cours_recurrent_id'),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'copied_from': session_key,
                    'copied_from_week': from_week.strftime('%Y-%m-%d')
                }

                dest_planning[new_session_key] = new_session_data
                copied_count += 1

            except Exception as e:
                errors.append(f"Erreur copie de {session_key}: {str(e)}")
                continue

        # Sauvegarder
        if not DataService.save_semaine_planning(to_week, dest_planning):
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500

        print(f"✅ Planning copié: {copied_count} sessions de {from_week_str} à {to_week_str}")

        response = {
            'success': True,
            'copied_count': copied_count,
            'skipped_count': skipped_count,
            'total_sessions': len(dest_planning),
            'from_week': from_week.strftime('%Y-%m-%d'),
            'to_week': to_week.strftime('%Y-%m-%d')
        }

        if errors:
            response['errors'] = errors

        return jsonify(response)

    except Exception as e:
        print(f"❌ Erreur copy_week: {e}")
        return jsonify({'error': 'Erreur lors de la copie du planning'}), 500


@planning_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Obtenir des statistiques sur le planning d'une semaine"""
    try:
        week_start_str = request.args.get('week_start')

        if not week_start_str:
            today = datetime.now().date()
            week_start = _get_week_start(today)
        else:
            try:
                week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
                week_start = _get_week_start(week_start)
            except ValueError:
                return jsonify({'error': 'Format de date invalide'}), 400

        planning = DataService.get_semaine_planning(week_start)

        # Statistiques
        stats = {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': (week_start + timedelta(days=6)).strftime('%Y-%m-%d'),
            'total_sessions': len(planning),
            'sessions_par_jour': {jour: 0 for jour in JOURS_SEMAINE},
            'cavaliers_uniques': set(),
            'equides_uniques': set(),
            'heures_totales': 0,
            'sessions_par_type': {},
            'sessions_from_recurrent': 0,
            'duree_moyenne': 0
        }

        total_duree = 0

        for session_data in planning.values():
            # Compter par jour
            jour = session_data.get('jour', '')
            if jour in stats['sessions_par_jour']:
                stats['sessions_par_jour'][jour] += 1

            # Cavaliers et équidés uniques
            stats['cavaliers_uniques'].update(session_data.get('cavaliers', []))
            stats['equides_uniques'].update(session_data.get('equides', []))

            # Durée
            duree = session_data.get('duree_minutes', 0)
            total_duree += duree
            stats['heures_totales'] += duree / 60

            # Compter par type
            type_cours = session_data.get('type_cours', 'cours')
            stats['sessions_par_type'][type_cours] = stats['sessions_par_type'].get(type_cours, 0) + 1

            # Compter les sessions issues de cours récurrents
            if session_data.get('cours_recurrent_id'):
                stats['sessions_from_recurrent'] += 1

        # Convertir les sets en nombres
        stats['cavaliers_uniques'] = len(stats['cavaliers_uniques'])
        stats['equides_uniques'] = len(stats['equides_uniques'])

        # Durée moyenne
        if len(planning) > 0:
            stats['duree_moyenne'] = round(total_duree / len(planning), 2)

        return jsonify(stats)

    except Exception as e:
        print(f"❌ Erreur get_statistics: {e}")
        return jsonify({'error': 'Erreur lors du calcul des statistiques'}), 500


@planning_bp.route('/conflicts', methods=['GET'])
def check_conflicts():
    """Vérifier les conflits dans le planning d'une semaine"""
    try:
        week_start_str = request.args.get('week_start')

        if not week_start_str:
            today = datetime.now().date()
            week_start = _get_week_start(today)
        else:
            try:
                week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
                week_start = _get_week_start(week_start)
            except ValueError:
                return jsonify({'error': 'Format de date invalide'}), 400

        planning = DataService.get_semaine_planning(week_start)

        conflicts = []

        # Organiser par jour
        sessions_by_day = {}
        for session_key, session_data in planning.items():
            date_str, _ = _parse_session_key(session_key)
            if date_str not in sessions_by_day:
                sessions_by_day[date_str] = []

            session_with_key = session_data.copy()
            session_with_key['key'] = session_key
            sessions_by_day[date_str].append(session_with_key)

        # Vérifier les chevauchements par jour
        for date_str, sessions in sessions_by_day.items():
            for i, session1 in enumerate(sessions):
                for session2 in sessions[i + 1:]:
                    try:
                        # Vérifier chevauchement horaire
                        h1_debut = _parse_time(session1.get('heure_debut', ''))
                        h2_debut = _parse_time(session2.get('heure_debut', ''))

                        if not h1_debut or not h2_debut:
                            continue

                        s1_debut = _time_to_minutes(h1_debut)
                        s1_fin = s1_debut + session1.get('duree_minutes', 60)
                        s2_debut = _time_to_minutes(h2_debut)
                        s2_fin = s2_debut + session2.get('duree_minutes', 60)

                        # Si chevauchement horaire
                        if (s1_debut < s2_fin) and (s2_debut < s1_fin):
                            # Vérifier conflits de cavaliers
                            cavaliers1 = set(session1.get('cavaliers', []))
                            cavaliers2 = set(session2.get('cavaliers', []))
                            conflict_cavaliers = cavaliers1.intersection(cavaliers2)

                            # Vérifier conflits d'équidés
                            equides1 = set(session1.get('equides', []))
                            equides2 = set(session2.get('equides', []))
                            conflict_equides = equides1.intersection(equides2)

                            if conflict_cavaliers or conflict_equides:
                                conflicts.append({
                                    'date': date_str,
                                    'session1': {
                                        'key': session1.get('key'),
                                        'heure_debut': session1.get('heure_debut'),
                                        'heure_fin': session1.get('heure_fin'),
                                        'cavaliers': session1.get('cavaliers_names', []),
                                        'equides': session1.get('equides_names', [])
                                    },
                                    'session2': {
                                        'key': session2.get('key'),
                                        'heure_debut': session2.get('heure_debut'),
                                        'heure_fin': session2.get('heure_fin'),
                                        'cavaliers': session2.get('cavaliers_names', []),
                                        'equides': session2.get('equides_names', [])
                                    },
                                    'conflict_cavaliers': list(conflict_cavaliers),
                                    'conflict_equides': list(conflict_equides)
                                })
                    except:
                        continue

        return jsonify({
            'week_start': week_start.strftime('%Y-%m-%d'),
            'conflicts_count': len(conflicts),
            'conflicts': conflicts
        })

    except Exception as e:
        print(f"❌ Erreur check_conflicts: {e}")
        return jsonify({'error': 'Erreur lors de la vérification des conflits'}), 500

