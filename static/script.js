// Planning de Cours d'Équitation - Script Principal

class PlanningManager {
    constructor() {
        this.currentWeek = this.getCurrentWeekStart();
        this.currentSession = null;
        this.courses = [];
        this.cavaliers = [];
        this.equides = [];
        this.creneaux = [];
        this.planning = {};
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadPlanning();
    }

    // ============= GESTION DES SEMAINES =============
    getCurrentWeekStart() {
        const today = new Date();
        const dayOfWeek = today.getDay();
        const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
        return new Date(today.setDate(diff));
    }

    getWeekDates(weekStart) {
        const dates = [];
        for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(weekStart.getDate() + i);
            dates.push(date);
        }
        return dates;
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    formatWeekDisplay(weekStart) {
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        const startStr = weekStart.toLocaleDateString('fr-FR', options);
        const endStr = weekEnd.toLocaleDateString('fr-FR', options);
        
        return `Semaine du ${startStr} au ${endStr}`;
    }

    // ============= CHARGEMENT DES DONNÉES =============
    async loadPlanning() {
        this.showLoading(true);
        
        try {
            const weekStartStr = this.formatDate(this.currentWeek);
            const response = await fetch(`/api/planning/week?week_start=${weekStartStr}`);
            const data = await response.json();
            
            if (response.ok) {
                this.courses = data.courses || [];
                this.cavaliers = data.cavaliers || [];
                this.equides = data.equides || [];
                this.creneaux = data.creneaux || [];
                this.planning = data.week_planning || {};
                
                this.updateWeekDisplay();
                this.renderPlanningGrid();
                this.updateDayHeaders();
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors du chargement:', error);
            this.showToast('Erreur de connexion au serveur', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // ============= AFFICHAGE =============
    updateWeekDisplay() {
        const weekTitle = document.getElementById('weekTitle');
        weekTitle.textContent = this.formatWeekDisplay(this.currentWeek);
    }

    updateDayHeaders() {
        const dates = this.getWeekDates(this.currentWeek);
        const dayColumns = document.querySelectorAll('.day-column');
        
        dates.forEach((date, index) => {
            const dayColumn = dayColumns[index];
            if (dayColumn) {
                const dateElement = dayColumn.querySelector('.day-date');
                if (dateElement) {
                    const options = { day: 'numeric', month: 'short' };
                    dateElement.textContent = date.toLocaleDateString('fr-FR', options);
                }
                
                // Ajouter la date comme data attribute
                dayColumn.setAttribute('data-date', this.formatDate(date));
                
                // Mettre en évidence le jour actuel
                const today = new Date();
                if (this.formatDate(date) === this.formatDate(today)) {
                    dayColumn.classList.add('today');
                } else {
                    dayColumn.classList.remove('today');
                }
            }
        });
    }

    renderPlanningGrid() {
        const grid = document.getElementById('planningGrid');
        grid.innerHTML = '';
        
        // Trier les créneaux par heure de début
        const sortedCreneaux = [...this.creneaux].sort((a, b) => 
            a.start.localeCompare(b.start)
        );
        
        sortedCreneaux.forEach(creneau => {
            if (!creneau.active) return;
            
            const row = document.createElement('div');
            row.className = 'planning-row';
            
            // Colonne temps
            const timeCell = document.createElement('div');
            timeCell.className = 'time-cell';
            timeCell.innerHTML = `
                <div class="time-label">${creneau.label}</div>
                <div class="time-range">${creneau.start} - ${creneau.end}</div>
            `;
            row.appendChild(timeCell);
            
            // Colonnes pour chaque jour
            const dates = this.getWeekDates(this.currentWeek);
            dates.forEach(date => {
                const dateStr = this.formatDate(date);
                const sessionKey = `${dateStr}_${creneau.id}`;
                const session = this.planning[sessionKey];
                
                const dayCell = document.createElement('div');
                dayCell.className = 'day-cell';
                dayCell.setAttribute('data-date', dateStr);
                dayCell.setAttribute('data-creneau', creneau.id);
                
                if (session) {
                    dayCell.innerHTML = this.renderSession(session);
                    dayCell.classList.add('has-session');
                } else {
                    dayCell.innerHTML = '<div class="empty-slot">Disponible</div>';
                }
                
                dayCell.addEventListener('click', () => this.openSessionModal(dateStr, creneau));
                row.appendChild(dayCell);
            });
            
            grid.appendChild(row);
        });
    }

    renderSession(session) {
        const course = this.courses.find(c => c.id === session.course_id);
        const courseColor = course ? course.color : '#ccc';
        
        const cavalierNames = (session.cavaliers || [])
            .map(id => this.cavaliers.find(c => c.id === id))
            .filter(c => c)
            .map(c => c.name)
            .slice(0, 3)
            .join(', ');
        
        const equideNames = (session.equides || [])
            .map(id => this.equides.find(e => e.id === id))
            .filter(e => e)
            .map(e => e.name)
            .slice(0, 2)
            .join(', ');
        
        return `
            <div class="session-card" style="background-color: ${courseColor}20; border-left: 4px solid ${courseColor};">
                <div class="session-course">${course ? course.name : 'Non défini'}</div>
                ${session.instructor ? `<div class="session-instructor">👨‍🏫 ${session.instructor}</div>` : ''}
                ${cavalierNames ? `<div class="session-cavaliers">👥 ${cavalierNames}${session.cavaliers.length > 3 ? '...' : ''}</div>` : ''}
                ${equideNames ? `<div class="session-equides">🐴 ${equideNames}${session.equides.length > 2 ? '...' : ''}</div>` : ''}
            </div>
        `;
    }

    // ============= MODALS =============
    openSessionModal(dateStr, creneau) {
        this.currentSession = { date: dateStr, creneau: creneau };
        
        const sessionKey = `${dateStr}_${creneau.id}`;
        const session = this.planning[sessionKey];
        
        // Titre du modal
        const date = new Date(dateStr + 'T00:00:00');
        const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
        const modalTitle = document.getElementById('modalTitle');
        modalTitle.textContent = `${date.toLocaleDateString('fr-FR', options)} - ${creneau.label}`;
        
        // Remplir les sélecteurs
        this.populateCourseSelect(session);
        this.populateCavaliersCheckboxes(session);
        this.populateEquidesCheckboxes(session);
        
        // Remplir les autres champs
        document.getElementById('instructorInput').value = session?.instructor || '';
        document.getElementById('notesTextarea').value = session?.notes || '';
        
        // Afficher le modal
        const modal = document.getElementById('sessionModal');
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
        
        // Gérer l'affichage du bouton supprimer
        const deleteBtn = document.getElementById('deleteSessionBtn');
        if (session) {
            deleteBtn.style.display = 'inline-block';
        } else {
            deleteBtn.style.display = 'none';
        }
        
        this.updateCharCounter();
    }

    populateCourseSelect(session) {
        const select = document.getElementById('courseSelect');
        select.innerHTML = '<option value="">-- Choisir un cours --</option>';
        
        this.courses.forEach(course => {
            if (!course.active) return;
            
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = course.name;
            option.selected = session && session.course_id === course.id;
            select.appendChild(option);
        });
        
        // Mettre à jour les infos du cours
        this.updateCourseInfo();
    }

    populateCavaliersCheckboxes(session) {
        const container = document.getElementById('cavaliersCheckboxes');
        container.innerHTML = '';
        
        const selectedCavaliers = new Set(session?.cavaliers || []);
        
        this.cavaliers.forEach(cavalier => {
            if (!cavalier.active) return;
            
            const div = document.createElement('div');
            div.className = 'checkbox-item';
            div.innerHTML = `
                <label>
                    <input type="checkbox" value="${cavalier.id}" ${selectedCavaliers.has(cavalier.id) ? 'checked' : ''}>
                    <span class="checkmark"></span>
                    ${cavalier.name}
                    <small>(${cavalier.level})</small>
                </label>
            `;
            container.appendChild(div);
        });
        
        this.updateCavaliersCount();
    }

    populateEquidesCheckboxes(session) {
        const container = document.getElementById('equidesCheckboxes');
        container.innerHTML = '';
        
        const selectedEquides = new Set(session?.equides || []);
        
        this.equides.forEach(equide => {
            if (!equide.active) return;
            
            const div = document.createElement('div');
            div.className = 'checkbox-item';
            div.innerHTML = `
                <label>
                    <input type="checkbox" value="${equide.id}" ${selectedEquides.has(equide.id) ? 'checked' : ''}>
                    <span class="checkmark"></span>
                    <div class="equide-info">
                        <span>${equide.name}</span>
                        <small>${equide.type} - ${equide.level}</small>
                    </div>
                </label>
            `;
            container.appendChild(div);
        });
        
        this.updateEquidesCount();
    }

    updateCourseInfo() {
        const courseId = parseInt(document.getElementById('courseSelect').value);
        const course = this.courses.find(c => c.id === courseId);
        const infoDiv = document.getElementById('courseInfo');
        
        if (course) {
            document.getElementById('courseDuration').textContent = course.duration;
            document.getElementById('courseMaxParticipants').textContent = course.max_participants;
            document.getElementById('courseMaxEquides').textContent = course.max_equides;
            infoDiv.style.display = 'block';
        } else {
            infoDiv.style.display = 'none';
        }
    }

    updateCavaliersCount() {
        const checked = document.querySelectorAll('#cavaliersCheckboxes input:checked');
        document.getElementById('cavaliersCount').textContent = checked.length;
    }

    updateEquidesCount() {
        const checked = document.querySelectorAll('#equidesCheckboxes input:checked');
        document.getElementById('equidesCount').textContent = checked.length;
    }

    updateCharCounter() {
        const textarea = document.getElementById('notesTextarea');
        const counter = document.getElementById('charCount');
        counter.textContent = textarea.value.length;
    }

    // ============= SAUVEGARDE =============
    async saveSession() {
        const courseId = parseInt(document.getElementById('courseSelect').value);
        if (!courseId) {
            this.showToast('Veuillez choisir un type de cours', 'error');
            return;
        }
        
        const course = this.courses.find(c => c.id === courseId);
        const selectedCavaliers = Array.from(document.querySelectorAll('#cavaliersCheckboxes input:checked'))
            .map(input => parseInt(input.value));
        const selectedEquides = Array.from(document.querySelectorAll('#equidesCheckboxes input:checked'))
            .map(input => parseInt(input.value));
        
        // Valider les capacités
        if (selectedCavaliers.length > course.max_participants) {
            this.showToast(`Trop de cavaliers: maximum ${course.max_participants}`, 'error');
            return;
        }
        
        if (selectedEquides.length > course.max_equides) {
            this.showToast(`Trop d'équidés: maximum ${course.max_equides}`, 'error');
            return;
        }
        
        const sessionData = {
            week_start: this.formatDate(this.currentWeek),
            date: this.currentSession.date,
            creneau_id: this.currentSession.creneau.id,
            course_id: courseId,
            cavaliers: selectedCavaliers,
            equides: selectedEquides,
            instructor: document.getElementById('instructorInput').value.trim(),
            notes: document.getElementById('notesTextarea').value.trim()
        };
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/planning/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sessionData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.planning = data.week_planning;
                this.renderPlanningGrid();
                this.closeModal('sessionModal');
                this.showToast('Séance enregistrée avec succès', 'success');
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            this.showToast('Erreur de connexion au serveur', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async deleteSession() {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cette séance ?')) {
            return;
        }
        
        const sessionData = {
            week_start: this.formatDate(this.currentWeek),
            date: this.currentSession.date,
            creneau_id: this.currentSession.creneau.id
        };
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/planning/session', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sessionData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.planning = data.week_planning;
                this.renderPlanningGrid();
                this.closeModal('sessionModal');
                this.showToast('Séance supprimée avec succès', 'success');
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la suppression:', error);
            this.showToast('Erreur de connexion au serveur', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // ============= NAVIGATION SEMAINE =============
    previousWeek() {
        this.currentWeek.setDate(this.currentWeek.getDate() - 7);
        this.loadPlanning();
    }

    nextWeek() {
        this.currentWeek.setDate(this.currentWeek.getDate() + 7);
        this.loadPlanning();
    }

    goToToday() {
        this.currentWeek = this.getCurrentWeekStart();
        this.loadPlanning();
    }

    // ============= COPIE SEMAINE =============
    openCopyWeekModal() {
        const modal = document.getElementById('copyWeekModal');
        const dateInput = document.getElementById('copyWeekDate');
        
        // Définir la date par défaut à la semaine prochaine
        const nextWeek = new Date(this.currentWeek);
        nextWeek.setDate(nextWeek.getDate() + 7);
        dateInput.value = this.formatDate(nextWeek);
        
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
    }

    async copyWeek() {
        const targetDate = document.getElementById('copyWeekDate').value;
        if (!targetDate) {
            this.showToast('Veuillez choisir une date de destination', 'error');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/planning/copy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_week: this.formatDate(this.currentWeek),
                    to_week: targetDate
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.closeModal('copyWeekModal');
                this.showToast(`Planning copié (${data.copied_sessions} séances)`, 'success');
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la copie:', error);
            this.showToast('Erreur de connexion au serveur', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async clearWeek() {
        if (!confirm('Êtes-vous sûr de vouloir vider toute cette semaine ? Cette action est irréversible.')) {
            return;
        }
        
        this.showLoading(true);
        
        try {
            // Supprimer toutes les séances de la semaine
            const promises = Object.keys(this.planning).map(async (sessionKey) => {
                const [date, creneauId] = sessionKey.split('_');
                const response = await fetch('/api/planning/session', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        week_start: this.formatDate(this.currentWeek),
                        date: date,
                        creneau_id: creneauId
                    })
                });
                return response.json();
            });
            
            await Promise.all(promises);
            
            this.planning = {};
            this.renderPlanningGrid();
            this.showToast('Semaine vidée avec succès', 'success');
        } catch (error) {
            console.error('Erreur lors du vidage:', error);
            this.showToast('Erreur lors du vidage de la semaine', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // ============= UTILITAIRES =============
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
    }

    showLoading(show) {
        const indicator = document.getElementById('loadingIndicator');
        indicator.style.display = show ? 'flex' : 'none';
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type}`;
        toast.style.display = 'block';
        
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }

    // ============= EVENTS =============
    bindEvents() {
        // Navigation semaine
        document.getElementById('prevWeek').addEventListener('click', () => this.previousWeek());
        document.getElementById('nextWeek').addEventListener('click', () => this.nextWeek());
        
        // Actions rapides
        document.getElementById('copyWeekBtn').addEventListener('click', () => this.openCopyWeekModal());
        document.getElementById('clearWeekBtn').addEventListener('click', () => this.clearWeek());
        
        // Modal session
        document.getElementById('saveSessionBtn').addEventListener('click', () => this.saveSession());
        document.getElementById('deleteSessionBtn').addEventListener('click', () => this.deleteSession());
        document.getElementById('closeModalBtn').addEventListener('click', () => this.closeModal('sessionModal'));
        
        // Changements dans le modal
        document.getElementById('courseSelect').addEventListener('change', () => this.updateCourseInfo());
        document.getElementById('cavaliersCheckboxes').addEventListener('change', () => this.updateCavaliersCount());
        document.getElementById('equidesCheckboxes').addEventListener('change', () => this.updateEquidesCount());
        document.getElementById('notesTextarea').addEventListener('input', () => this.updateCharCounter());
        
        // Modal copie semaine
        document.getElementById('confirmCopyBtn').addEventListener('click', () => this.copyWeek());
        document.getElementById('cancelCopyBtn').addEventListener('click', () => this.closeModal('copyWeekModal'));
        
        // Fermeture des modals
        document.querySelectorAll('.modal .close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal').id);
            });
        });
        
        // Fermer les modals en cliquant à l'extérieur
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
        
        // Raccourcis clavier
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
                    this.closeModal(modal.id);
                });
            }
            
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        this.previousWeek();
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        this.nextWeek();
                        break;
                }
            }
        });
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    window.planningManager = new PlanningManager();
});