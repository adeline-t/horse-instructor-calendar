// Gestion des Cours - Script

class CoursesManager {
    constructor() {
        this.courses = [];
        this.currentCourse = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCourses();
    }

    // ============= CHARGEMENT DES DONNÉES =============
    async loadCourses() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/courses');
            const data = await response.json();
            
            if (response.ok) {
                this.courses = data || [];
                this.renderCoursesList();
                this.updateStats();
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
    renderCoursesList() {
        const container = document.getElementById('coursesList');
        const emptyMessage = document.getElementById('noCoursesMessage');
        
        if (this.courses.length === 0) {
            container.innerHTML = '';
            emptyMessage.style.display = 'block';
            return;
        }
        
        emptyMessage.style.display = 'none';
        container.innerHTML = '';
        
        this.courses.forEach(course => {
            const card = this.createCourseCard(course);
            container.appendChild(card);
        });
    }

    createCourseCard(course) {
        const card = document.createElement('div');
        card.className = `course-card ${!course.active ? 'inactive' : ''}`;
        card.innerHTML = `
            <div class="course-header">
                <div class="course-info">
                    <h3 class="course-name">
                        <span class="color-indicator" style="background-color: ${course.color}"></span>
                        ${course.name}
                    </h3>
                </div>
                <div class="course-status">
                    <span class="status-badge ${course.active ? 'active' : 'inactive'}">
                        ${course.active ? 'Actif' : 'Inactif'}
                    </span>
                </div>
            </div>
            <div class="course-details">
                <div class="course-stat">
                    <span class="stat-label">Durée:</span>
                    <span class="stat-value">${course.duration} min</span>
                </div>
                <div class="course-stat">
                    <span class="stat-label">Max participants:</span>
                    <span class="stat-value">${course.max_participants}</span>
                </div>
                <div class="course-stat">
                    <span class="stat-label">Max équidés:</span>
                    <span class="stat-value">${course.max_equides}</span>
                </div>
            </div>
            <div class="course-color-preview">
                <div class="color-sample" style="background-color: ${course.color}"></div>
                <span class="color-code">${course.color}</span>
            </div>
            <div class="course-actions">
                <button class="btn btn-secondary edit-btn" data-id="${course.id}">
                    <span class="btn-icon">✏️</span>
                    Modifier
                </button>
                <button class="btn btn-danger delete-btn" data-id="${course.id}">
                    <span class="btn-icon">🗑️</span>
                    Supprimer
                </button>
            </div>
        `;
        
        // Ajouter les événements
        card.querySelector('.edit-btn').addEventListener('click', () => this.editCourse(course));
        card.querySelector('.delete-btn').addEventListener('click', () => this.deleteCourse(course));
        
        return card;
    }

    updateStats() {
        const totalCourses = this.courses.length;
        const activeCourses = this.courses.filter(c => c.active).length;
        const avgDuration = this.courses.length > 0 
            ? Math.round(this.courses.reduce((sum, c) => sum + c.duration, 0) / this.courses.length)
            : 0;
        const totalCapacity = this.courses.reduce((sum, c) => sum + c.max_participants, 0);
        
        document.getElementById('totalCourses').textContent = totalCourses;
        document.getElementById('activeCourses').textContent = activeCourses;
        document.getElementById('avgDuration').textContent = avgDuration;
        document.getElementById('totalCapacity').textContent = totalCapacity;
    }

    // ============= MODALS =============
    openCourseModal(course = null) {
        this.currentCourse = course;
        
        const modal = document.getElementById('courseModal');
        const form = document.getElementById('courseForm');
        const title = document.getElementById('modalTitle');
        
        if (course) {
            title.textContent = 'Modifier un cours';
            document.getElementById('courseName').value = course.name;
            document.getElementById('courseDuration').value = course.duration;
            document.getElementById('courseMaxParticipants').value = course.max_participants;
            document.getElementById('courseMaxEquides').value = course.max_equides;
            document.getElementById('courseColor').value = course.color;
            document.getElementById('courseColorText').value = course.color;
            document.getElementById('courseActive').checked = course.active;
        } else {
            title.textContent = 'Ajouter un cours';
            form.reset();
            document.getElementById('courseDuration').value = 60;
            document.getElementById('courseMaxParticipants').value = 8;
            document.getElementById('courseMaxEquides').value = 6;
            document.getElementById('courseColor').value = '#90EE90';
            document.getElementById('courseColorText').value = '#90EE90';
            document.getElementById('courseActive').checked = true;
        }
        
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
    }

    openDeleteModal(course) {
        this.currentCourse = course;
        
        const modal = document.getElementById('deleteCourseModal');
        document.getElementById('deleteCourseName').textContent = course.name;
        
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
    }

    // ============= SAUVEGARDE =============
    async saveCourse() {
        const form = document.getElementById('courseForm');
        const formData = new FormData(form);
        
        const courseData = {
            name: formData.get('name').trim(),
            duration: parseInt(formData.get('duration')),
            max_participants: parseInt(formData.get('max_participants')),
            max_equides: parseInt(formData.get('max_equides')),
            color: formData.get('color'),
            active: formData.get('active') === 'on'
        };
        
        // Validation
        if (!courseData.name) {
            this.showToast('Le nom du cours est requis', 'error');
            return;
        }
        
        if (!courseData.duration || courseData.duration < 30 || courseData.duration > 180) {
            this.showToast('La durée doit être entre 30 et 180 minutes', 'error');
            return;
        }
        
        if (!courseData.max_participants || courseData.max_participants < 1 || courseData.max_participants > 20) {
            this.showToast('Le nombre max de participants doit être entre 1 et 20', 'error');
            return;
        }
        
        if (!courseData.max_equides || courseData.max_equides < 1 || courseData.max_equides > 20) {
            this.showToast('Le nombre max d\'équidés doit être entre 1 et 20', 'error');
            return;
        }
        
        this.showLoading(true);
        
        try {
            let response;
            if (this.currentCourse) {
                // Modification
                response = await fetch(`/api/courses/${this.currentCourse.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(courseData)
                });
            } else {
                // Ajout
                response = await fetch('/api/courses', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(courseData)
                });
            }
            
            const data = await response.json();
            
            if (response.ok) {
                this.courses = data.courses;
                this.renderCoursesList();
                this.updateStats();
                this.closeModal('courseModal');
                this.showToast(`Cours ${this.currentCourse ? 'modifié' : 'ajouté'} avec succès`, 'success');
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

    async deleteCourse() {
        this.showLoading(true);
        
        try {
            const response = await fetch(`/api/courses/${this.currentCourse.id}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.courses = data.courses;
                this.renderCoursesList();
                this.updateStats();
                this.closeModal('deleteCourseModal');
                this.showToast('Cours supprimé avec succès', 'success');
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

    // ============= UTILITAIRES =============
    editCourse(course) {
        this.openCourseModal(course);
    }

    updateColorText() {
        const colorInput = document.getElementById('courseColor');
        const colorText = document.getElementById('courseColorText');
        colorText.value = colorInput.value.toUpperCase();
    }

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
        // Actions principales
        document.getElementById('addCourseBtn').addEventListener('click', () => this.openCourseModal());
        
        // Formulaire
        document.getElementById('courseForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCourse();
        });
        
        // Couleur
        document.getElementById('courseColor').addEventListener('input', () => this.updateColorText());
        
        // Modals
        document.getElementById('cancelCourseBtn').addEventListener('click', () => this.closeModal('courseModal'));
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => this.deleteCourse());
        document.getElementById('cancelDeleteBtn').addEventListener('click', () => this.closeModal('deleteCourseModal'));
        
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
                    case 'n':
                        e.preventDefault();
                        this.openCourseModal();
                        break;
                }
            }
        });
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    window.coursesManager = new CoursesManager();
});