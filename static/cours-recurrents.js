// Gestion des Cours Récurrents - Script

class CoursRecurrentsManager {
    constructor() {
        this.cours = [];
        this.currentCourse = null;
        this.currentFilter = 'all';
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCours();
    }

    // ============= CHARGEMENT DES DONNÉES =============
    async loadCours() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/cours-recurrents');
            const data = await response.json();
            
            if (response.ok) {
                this.cours = data || [];
                this.renderCoursList();
                this.updateStats();
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors du chargement des cours:', error);
            this.showToast('Erreur lors du chargement des cours', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // ============= GESTION DES ÉVÉNEMENTS =============
    bindEvents() {
        // Bouton ajouter
        document.getElementById('addCourseBtn').addEventListener('click', () => {
            this.openCourseModal();
        });

        // Formulaire
        document.getElementById('courseForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCourse();
        });

        // Filtres
        document.querySelectorAll('.filter-buttons button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-buttons button').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentFilter = e.target.dataset.filter;
                this.renderCoursList();
            });
        });

        // Fermeture modale au clic extérieur
        document.getElementById('courseModal').addEventListener('click', (e) => {
            if (e.target.id === 'courseModal') {
                this.closeCourseModal();
            }
        });
    }

    // ============= RENDU =============
    renderCoursList() {
        const container = document.getElementById('coursesList');
        
        let filteredCours = this.cours;
        if (this.currentFilter === 'active') {
            filteredCours = this.cours.filter(c => c.actif !== false);
        } else if (this.currentFilter === 'inactive') {
            filteredCours = this.cours.filter(c => c.actif === false);
        }

        if (filteredCours.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔄</div>
                    <h3>Aucun cours récurrent</h3>
                    <p>${this.currentFilter !== 'all' ? 'Aucun cours ne correspond à ce filtre' : 'Commencez par ajouter un cours récurrent'}</p>
                    ${this.currentFilter === 'all' ? '<button class="btn btn-primary" onclick="courseManager.openCourseModal()">Ajouter un cours</button>' : ''}
                </div>
            `;
            return;
        }

        const coursesHTML = filteredCours.map(course => `
            <div class="course-item ${!course.actif ? 'inactive' : ''}" data-id="${course.id}">
                <div class="course-header">
                    <div class="course-info">
                        <h4 class="course-name">${course.nom}</h4>
                        <div class="course-details">
                            <span class="course-day">${this.capitalizeFirst(course.jour)}</span>
                            <span class="course-time">${course.heure}</span>
                            <span class="course-duration">${course.duree || 60} min</span>
                        </div>
                        ${course.moniteur ? `<div class="course-instructor">Moniteur: ${course.moniteur}</div>` : ''}
                        ${course.description ? `<div class="course-description">${course.description}</div>` : ''}
                    </div>
                    <div class="course-actions">
                        <button class="btn btn-small btn-edit" onclick="courseManager.editCourse(${course.id})" title="Modifier">
                            ✏️
                        </button>
                        <button class="btn btn-small btn-toggle" onclick="courseManager.toggleCourse(${course.id})" title="${course.actif ? 'Désactiver' : 'Activer'}">
                            ${course.actif ? '⏸️' : '▶️'}
                        </button>
                        <button class="btn btn-small btn-delete" onclick="courseManager.deleteCourse(${course.id})" title="Supprimer">
                            🗑️
                        </button>
                    </div>
                </div>
                <div class="course-color-bar" style="background-color: ${course.couleur || '#90EE90'}"></div>
            </div>
        `).join('');

        container.innerHTML = coursesHTML;
    }

    updateStats() {
        const total = this.cours.length;
        const active = this.cours.filter(c => c.actif !== false).length;
        
        document.getElementById('totalCourses').textContent = total;
        document.getElementById('activeCourses').textContent = active;
    }

    // ============= MODALES =============
    openCourseModal(course = null) {
        this.currentCourse = course;
        const modal = document.getElementById('courseModal');
        const form = document.getElementById('courseForm');
        const title = document.getElementById('modalTitle');
        
        if (course) {
            title.textContent = 'Modifier le cours récurrent';
            form.nom.value = course.nom || '';
            form.jour.value = course.jour || '';
            form.heure.value = course.heure || '';
            form.duree.value = course.duree || 60;
            form.moniteur.value = course.moniteur || '';
            form.couleur.value = course.couleur || '#90EE90';
            form.description.value = course.description || '';
            form.actif.checked = course.actif !== false;
        } else {
            title.textContent = 'Ajouter un cours récurrent';
            form.reset();
            form.couleur.value = '#90EE90';
            form.actif.checked = true;
        }
        
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('show'), 10);
    }

    closeCourseModal() {
        const modal = document.getElementById('courseModal');
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
        this.currentCourse = null;
    }

    // ============= ACTIONS =============
    async saveCourse() {
        const form = document.getElementById('courseForm');
        const formData = new FormData(form);
        
        const courseData = {
            nom: formData.get('nom').trim(),
            jour: formData.get('jour'),
            heure: formData.get('heure'),
            duree: parseInt(formData.get('duree')) || 60,
            moniteur: formData.get('moniteur').trim(),
            couleur: formData.get('couleur'),
            description: formData.get('description').trim(),
            actif: formData.get('actif') === 'on'
        };

        // Validation
        if (!courseData.nom || !courseData.jour || !courseData.heure) {
            this.showToast('Les champs nom, jour et heure sont obligatoires', 'error');
            return;
        }

        this.showLoading(true);
        
        try {
            const url = this.currentCourse ? `/api/cours-recurrents/${this.currentCourse.id}` : '/api/cours-recurrents';
            const method = this.currentCourse ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(courseData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showToast(this.currentCourse ? 'Cours modifié avec succès' : 'Cours ajouté avec succès', 'success');
                this.closeCourseModal();
                await this.loadCours();
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            this.showToast('Erreur lors de la sauvegarde', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async editCourse(id) {
        const course = this.cours.find(c => c.id === id);
        if (course) {
            this.openCourseModal(course);
        }
    }

    async toggleCourse(id) {
        const course = this.cours.find(c => c.id === id);
        if (!course) return;
        
        const newStatus = !course.actif;
        
        this.showLoading(true);
        
        try {
            const response = await fetch(`/api/cours-recurrents/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ actif: newStatus })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showToast(`Cours ${newStatus ? 'activé' : 'désactivé'} avec succès`, 'success');
                await this.loadCours();
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors du changement de statut:', error);
            this.showToast('Erreur lors du changement de statut', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async deleteCourse(id) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce cours récurrent ?')) {
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch(`/api/cours-recurrents/${id}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showToast('Cours supprimé avec succès', 'success');
                await this.loadCours();
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la suppression:', error);
            this.showToast('Erreur lors de la suppression', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // ============= UTILITAIRES =============
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

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Fonctions globales pour les onclick
let courseManager;

function closeCourseModal() {
    if (courseManager) {
        courseManager.closeCourseModal();
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    courseManager = new CoursRecurrentsManager();
});