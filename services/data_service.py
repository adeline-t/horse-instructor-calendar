import json
import os
from datetime import datetime, timedelta, date as date_cls
from typing import Any, Dict, List, Optional
from dateutil.relativedelta import relativedelta
from config import Config


def _safe_json_read(path: str, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Basic shape validation
            if isinstance(default, list) and not isinstance(data, list):
                return default
            if isinstance(default, dict) and not isinstance(data, dict):
                return default
            return data
    except Exception as e:
        print(f"❌ Erreur lecture JSON '{path}': {e}")
        return default


def _safe_json_write(path: str, payload) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erreur écriture JSON '{path}': {e}")
        return False


def _parse_date_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.strptime(s, '%Y-%m-%d')
    except Exception:
        return None


class DataService:
    """Service pour gérer la lecture/écriture des fichiers du système avancé"""

    # ============= CAVALIERS =============
    @staticmethod
    def read_cavaliers() -> List[Dict[str, Any]]:
        """Lire le fichier cavaliers.json"""
        data = _safe_json_read(Config.CAVALIERS_FILE, [])
        return data if isinstance(data, list) else []

    @staticmethod
    def write_cavaliers(cavaliers: List[Dict[str, Any]]) -> bool:
        """Écrire dans le fichier cavaliers.json"""
        ok = _safe_json_write(Config.CAVALIERS_FILE, cavaliers)
        if ok:
            print(f"✅ Cavaliers sauvegardés : {len(cavaliers)} entrées")
        return ok

    @staticmethod
    def is_cavalier_actif_period(cavalier: Dict[str, Any], d: date_cls) -> bool:
        """Vérifier si un cavalier est actif pour une date donnée"""
        date_debut = _parse_date_iso(cavalier.get('date_debut'))
        date_fin = _parse_date_iso(cavalier.get('date_fin'))

        # Si date_debut définie et d avant début -> inactif
        if date_debut and d < date_debut.date():
            return False

        # Si date_fin définie et d après fin -> inactif
        if date_fin and d > date_fin.date():
            return False

        return True

    @staticmethod
    def get_cavaliers_actifs(at_date: Optional[date_cls] = None) -> List[Dict[str, Any]]:
        """Récupérer les cavaliers actifs à une date donnée"""
        cavaliers = DataService.read_cavaliers()
        if at_date is None:
            at_date = date_cls.today()
        return [
            c for c in cavaliers
            if c.get('actif', True) and DataService.is_cavalier_actif_period(c, at_date)
        ]

    # ============= ÉQUIDÉS =============
    @staticmethod
    def read_equides() -> List[Dict[str, Any]]:
        """Lire le fichier equides.json"""
        data = _safe_json_read(Config.EQUIDES_FILE, [])
        return data if isinstance(data, list) else []

    @staticmethod
    def write_equides(equides: List[Dict[str, Any]]) -> bool:
        """Écrire dans le fichier equides.json"""
        ok = _safe_json_write(Config.EQUIDES_FILE, equides)
        if ok:
            print(f"✅ Équidés sauvegardés : {len(equides)} entrées")
        return ok

    @staticmethod
    def get_equides_actifs() -> List[Dict[str, Any]]:
        """Récupérer les équidés actifs"""
        equides = DataService.read_equides()
        return [e for e in equides if e.get('actif', True)]

    @staticmethod
    def get_equides_disponibles_pour_cavalier(cavalier_id: int, incl_laury_owned: bool = True) -> List[Dict[str, Any]]:
        """
        Récupérer les équidés disponibles pour un cavalier.
        Logique:
        - Propriétaire direct (proprietaire_id == cavalier_id) -> disponible
        - Heures allouées dans equide.heures_par_cavalier -> disponible
        - Optionnel: chevaux owned_by_laury -> disponibles à tous (incl_laury_owned=True)
        """
        equides = DataService.get_equides_actifs()
        disponibles = []
        cid = str(cavalier_id)

        for equide in equides:
            if equide.get('proprietaire_id') is not None and str(equide.get('proprietaire_id')) == cid:
                disponibles.append(equide)
                continue

            heures_map = equide.get('heures_par_cavalier', {}) or {}
            if cid in heures_map:
                disponibles.append(equide)
                continue

            if incl_laury_owned and equide.get('owned_by_laury', False):
                disponibles.append(equide)
                continue

        return disponibles

    # ============= COURS RÉCURRENTS =============
    @staticmethod
    def read_cours_recurrents() -> List[Dict[str, Any]]:
        """Lire le fichier cours_recurrents.json"""
        data = _safe_json_read(Config.COURS_RECURRENTS_FILE, [])
        return data if isinstance(data, list) else []

    @staticmethod
    def write_cours_recurrents(cours_recurrents: List[Dict[str, Any]]) -> bool:
        """Écrire dans le fichier cours_recurrents.json"""
        ok = _safe_json_write(Config.COURS_RECURRENTS_FILE, cours_recurrents)
        if ok:
            print(f"✅ Cours récurrents sauvegardés : {len(cours_recurrents)} types")
        return ok

    @staticmethod
    def get_cours_recurrents_actifs() -> List[Dict[str, Any]]:
        """Récupérer les cours récurrents actifs"""
        cours = DataService.read_cours_recurrents()
        return [c for c in cours if c.get('actif', True)]

    @staticmethod
    def generer_cours_semaine(date_debut_semaine: date_cls) -> List[Dict[str, Any]]:
        """Générer les cours de la semaine à partir des cours récurrents"""
        cours_recurrents = DataService.get_cours_recurrents_actifs()
        semaine_cours: List[Dict[str, Any]] = []

        jours_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        jour_to_index = {j: i for i, j in enumerate(jours_fr)}

        for cr in cours_recurrents:
            j = cr.get('jour', '').lower()
            if j not in jour_to_index:
                continue
            date_cours = date_debut_semaine + timedelta(days=jour_to_index[j])

            cours_genere = {
                'id': f"rec_{cr.get('id')}_{date_cours.strftime('%Y-%m-%d')}",
                'date': date_cours.strftime('%Y-%m-%d'),
                'heure': cr.get('heure'),
                'duree': cr.get('duree'),
                'moniteur': cr.get('moniteur'),
                'nom': cr.get('nom'),
                'description': cr.get('description', ''),
                'couleur': cr.get('couleur', '#CCCCCC'),
                'recurrent_id': cr.get('id'),
                'cavaliers': [],
                'equides': [],
                'notes': '',
                'ponctuel': False,
                'modifie': False
            }
            semaine_cours.append(cours_genere)

        return semaine_cours

    # ============= DISPONIBILITÉS =============
    @staticmethod
    def read_disponibilites() -> Dict[str, List[Dict[str, str]]]:
        """
        Lire le fichier disponibilites.json.
        Conserve la structure par jour: [{start, end, label}, ...]
        """
        default = getattr(Config, 'DEFAULT_CRENEAUX_PAR_JOUR', {})
        data = _safe_json_read(Config.DISPONIBILITES_FILE, default if isinstance(default, dict) else {})
        return data if isinstance(data, dict) else (default if isinstance(default, dict) else {})

    @staticmethod
    def write_disponibilites(disponibilites: Dict[str, List[Dict[str, str]]]) -> bool:
        """Écrire dans le fichier disponibilites.json"""
        ok = _safe_json_write(Config.DISPONIBILITES_FILE, disponibilites)
        if ok:
            print("✅ Disponibilités sauvegardées")
        return ok

    # ============= PLANNING =============
    @staticmethod
    def read_planning() -> Dict[str, Dict[str, Any]]:
        """Lire le fichier planning.json"""
        data = _safe_json_read(Config.PLANNING_FILE, {})
        return data if isinstance(data, dict) else {}

    @staticmethod
    def write_planning(planning: Dict[str, Dict[str, Any]]) -> bool:
        """Écrire dans le fichier planning.json"""
        ok = _safe_json_write(Config.PLANNING_FILE, planning)
        if ok:
            print("✅ Planning sauvegardé")
        return ok

    @staticmethod
    def _week_key(d: date_cls) -> str:
        # ISO week-year to avoid %Y-%W pitfalls with year overlaps
        iso_year, iso_week, _ = d.isocalendar()
        return f"{iso_year}-{iso_week:02d}"

    @staticmethod
    def get_semaine_planning(date_debut_semaine: date_cls) -> List[Dict[str, Any]]:
        """Récupérer le planning pour une semaine donnée et fusionner récurrents + ponctuels/modifs"""
        planning = DataService.read_planning()
        semaine_key = DataService._week_key(date_debut_semaine)
        semaine_data: Dict[str, Any] = planning.get(semaine_key, {}) or {}

        # Générer les cours récurrents de la semaine
        generated = DataService.generer_cours_semaine(date_debut_semaine)

        # Indexer par id pour permettre remplacement par modifs
        by_id = {c['id']: c for c in generated}

        # Parcours des entrées de la semaine
        for k, entry in semaine_data.items():
            if k.startswith('ponctuel_'):
                # Cours ponctuel déjà complet
                if isinstance(entry, dict):
                    entry.setdefault('ponctuel', True)
                    entry.setdefault('modifie', False)
                    by_id[entry.get('id', k)] = entry
            elif k.startswith('modif_'):
                # Modification d’un cours récurrent
                original_id = k.replace('modif_', '')
                if original_id in by_id and isinstance(entry, dict):
                    # Fusion: les champs fournis dans entry priment
                    merged = {**by_id[original_id], **entry}
                    merged['modifie'] = True
                    merged['ponctuel'] = False
                    by_id[original_id] = merged
            else:
                # Compat: si des clés libres existent (ex: un id direct)
                if isinstance(entry, dict):
                    by_id[k] = entry

        return list(by_id.values())

    @staticmethod
    def save_semaine_planning(date_debut_semaine: date_cls, semaine_data: Dict[str, Any]) -> bool:
        """Sauvegarder le planning pour une semaine donnée"""
        planning = DataService.read_planning()
        semaine_key = DataService._week_key(date_debut_semaine)
        planning[semaine_key] = semaine_data
        return DataService.write_planning(planning)


    # ============= STATISTIQUES =============
    @staticmethod
    def read_statistiques() -> Dict[str, Any]:
        """Lire le fichier statistiques.json"""
        data = _safe_json_read(Config.STATISTIQUES_FILE, {})
        return data if isinstance(data, dict) else {}

    @staticmethod
    def write_statistiques(statistiques: Dict[str, Any]) -> bool:
        """Écrire dans le fichier statistiques.json"""
        return _safe_json_write(Config.STATISTIQUES_FILE, statistiques)

    @staticmethod
    def calculer_statistiques_mois(annee: int, mois: int) -> Dict[str, Any]:
        """
        Calculer des stats mensuelles basiques à partir des cours générés/planifiés.
        Hypothèse: on considère les cours (récurrents + ponctuels + modifiés) du mois.
        Sortie possible:
        - total_cours
        - total_heures
        - par_moniteur: nombre de cours et heures
        - par_type: nombre de cours et heures (via champ 'nom')
        Note: cette implémentation parcourt toutes les semaines stockées, filtre par mois/année.
        """
        planning = DataService.read_planning()

        def parse_date(dstr: str) -> Optional[datetime]:
            try:
                return datetime.strptime(dstr, '%Y-%m-%d')
            except Exception:
                return None

        total_cours = 0
        total_heures = 0.0
        par_moniteur: Dict[str, Dict[str, float]] = {}
        par_type: Dict[str, Dict[str, float]] = {}

        # On doit reconstruire les cours de toutes les semaines, puis filtrer au mois
        # Pour chaque entrée de semaine, produire la liste fusionnée
        for week_key, semaine_data in (planning or {}).items():
            # Tenter de déduire la date de début de semaine depuis la clé ISO si possible
            # La clé est "YYYY-WW". On ne la convertit pas; on va juste lire les entrées et
            # compter sur les champs 'date' à l’intérieur.
            # semaine_data est un dict de {clé: cours ou modif...}
            if not isinstance(semaine_data, dict):
                continue

            # Nous devons reconstituer les cours fusionnés de cette semaine.
            # Sans date_debut_semaine exacte, on ne peut pas régénérer correctement les récurrents ici.
            # Approach: compter seulement ce qui est explicitement stocké (ponctuel_X ou modif_rec_...),
            # sinon fallback: ignorer si pas explicite. Pour une stats plus complète, l’app devrait
            # sauvegarder les cours effectifs de la semaine (clé unique par cours) dans le planning.
            # Ici, on prend uniquement les entrées dict possédant une 'date' (déjà fusionnées ou ponctuelles)
            for k, entry in semaine_data.items():
                if not isinstance(entry, dict):
                    continue
                d = parse_date(entry.get('date', ''))
                if not d or d.year != annee or d.month == 0 or d.month != mois:
                    continue

                duree_min = entry.get('duree') or 0
                duree_h = float(duree_min) / 60.0 if isinstance(duree_min, (int, float)) else 0.0

                total_cours += 1
                total_heures += duree_h

                moniteur = entry.get('moniteur') or 'Inconnu'
                par_moniteur.setdefault(moniteur, {'cours': 0, 'heures': 0.0})
                par_moniteur[moniteur]['cours'] += 1
                par_moniteur[moniteur]['heures'] += duree_h

                type_nom = entry.get('nom') or 'Sans nom'
                par_type.setdefault(type_nom, {'cours': 0, 'heures': 0.0})
                par_type[type_nom]['cours'] += 1
                par_type[type_nom]['heures'] += duree_h

        stats = {
            'annee': annee,
            'mois': mois,
            'total_cours': total_cours,
            'total_heures': round(total_heures, 2),
            'par_moniteur': par_moniteur,
            'par_type': par_type,
            'generated_at': datetime.now().isoformat(timespec='seconds')
        }
        return stats

    # ============= DEBUG FILE INFO =============
    @staticmethod
    def get_file_info() -> Dict[str, Any]:
        """Obtenir des informations sur les fichiers (debug)"""
        def _info(path):
            return {
                'exists': os.path.exists(path),
                'path': path,
                'readable': os.path.exists(path) and os.access(path, os.R_OK),
                'writable': os.path.exists(path) and os.access(path, os.W_OK),
            }

        info = {
            'cavaliers': _info(Config.CAVALIERS_FILE),
            'equides': _info(Config.EQUIDES_FILE),
            'cours_recurrents': _info(Config.COURS_RECURRENTS_FILE),
            'planning': _info(Config.PLANNING_FILE),
            'disponibilites': _info(Config.DISPONIBILITES_FILE),
            'heures_cavaliers': _info(Config.HEURES_CAVALIERS_FILE),
            'types_forfaits': _info(getattr(Config, 'TYPES_FORFAITS_FILE', '')),
            'statistiques': _info(Config.STATISTIQUES_FILE),
            'data_dir': {
                'exists': os.path.exists(Config.DATA_DIR),
                'path': Config.DATA_DIR,
                'writable': os.path.exists(Config.DATA_DIR) and os.access(Config.DATA_DIR, os.W_OK),
            }
        }
        return info


    # Ajouter ces méthodes à DataService

    @staticmethod
    def read_heures_allocations() -> list:
        """Lire le fichier des allocations d'heures"""
        filepath = os.path.join(Config.DATA_DIR, 'heures_allocations.json')
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur lecture heures_allocations.json: {e}")
            return []


    @staticmethod
    def write_heures_allocations(heures: list) -> bool:
        """Écrire dans le fichier des allocations d'heures"""
        filepath = os.path.join(Config.DATA_DIR, 'heures_allocations.json')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(heures, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erreur écriture heures_allocations.json: {e}")
            return False
