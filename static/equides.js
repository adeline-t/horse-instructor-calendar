// Gestion des Équidés - Script

class EquidesManager {
    constructor() {
        this.equides = [];
        this.filteredEquides = [];
        this.currentEquide = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadEquides();
    }

    // ============= CHARGEMENT DES DONNÉES =============
    async loadEquides() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/equides');
            const data = await response.json();
            
            if (response.ok) {
                this.equides = data || [];
                this.applyFilters();
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

    // ============= FILTRES =============
applyFilters() {
  const typeFilter = document.getElementById('typeFilter').value;
  const activeFilter = document.getElementById('activeFilter').value;

  this.filteredEquides = this.equides.filter(equide => {
    if (typeFilter && equide.type !== typeFilter) return false;
    if (activeFilter !== '' && (equide.actif !== (activeFilter === 'true'))) return false;
    return true;
  });

  this.renderEquidesList();
}


    // ============= AFFICHAGE =============
    renderEquidesList() {
        const container = document.getElementById('equidesList');
        const emptyMessage = document.getElementById('noEquidesMessage');
        
        if (this.filteredEquides.length === 0) {
            container.innerHTML = '';
            emptyMessage.style.display = 'block';
            return;
        }
        
        emptyMessage.style.display = 'none';
        container.innerHTML = '';
        
        this.filteredEquides.forEach(equide => {
            const card = this.createEquideCard(equide);
            container.appendChild(card);
        });
    }

    createEquideCard(equide) {
  const card = document.createElement('div');
  card.className = `equide-card ${equide.actif ? '' : 'inactive'}`;
  card.innerHTML = `
    <div class="equide-header">
      <div class="equide-info">
        <h3 class="equide-name">🐴 ${equide.name}</h3>
        <div class="equide-details">
          <span class="equide-type">${equide.type}</span>
          ${equide.proprietaire_name ? `<span class="equide-owner">Propriétaire: ${equide.proprietaire_name}</span>` : ''}
          ${equide.owned_by_laury ? `<span class="equide-owner">Appartient à Laury</span>` : ''}
        </div>
      </div>
      <div class="equide-status">
        <span class="status-badge ${equide.actif ? 'active' : 'inactive'}">
          ${equide.actif ? 'Actif' : 'Inactif'}
        </span>
      </div>
    </div>
    ${equide.notes ? `<div class="course-color-preview"><span class="color-code">${equide.notes}</span></div>` : ''}
    <div class="equide-actions">
      <button class="btn btn-secondary edit-btn" data-id="${equide.id}">
        <span class="btn-icon">✏️</span> Modifier
      </button>
      <button class="btn btn-danger delete-btn" data-id="${equide.id}">
        <span class="btn-icon">🗑️</span> Supprimer
      </button>
    </div>
  `;
  card.querySelector('.edit-btn').addEventListener('click', () => this.editEquide(equide));
  card.querySelector('.delete-btn').addEventListener('click', () => this.deleteEquide(equide));
  return card;
}


updateStats() {
  const totalEquides = this.equides.length;
  const activeEquides = this.equides.filter(e => e.actif).length;
  const chevauxCount = this.equides.filter(e => e.type === 'Cheval').length;
  const poneysCount = this.equides.filter(e => e.type === 'Poney').length;
  document.getElementById('totalEquides').textContent = totalEquides;
  document.getElementById('activeEquides').textContent = activeEquides;
  document.getElementById('chevauxCount').textContent = chevauxCount;
  document.getElementById('poneysCount').textContent = poneysCount;
}


    // ============= MODALS =============
    openEquideModal(equide = null) {
        this.currentEquide = equide;
        
        const modal = document.getElementById('equideModal');
        const form = document.getElementById('equideForm');
        const title = document.getElementById('modalTitle');
        
        if (equide) {
            title.textContent = 'Modifier un équidé';
            document.getElementById('equideName').value = equide.name;
            document.getElementById('equideType').value = equide.type;
            document.getElementById('equideRace').value = equide.race || '';
            document.getElementById('equideLevel').value = equide.level;
            document.getElementById('equideColor').value = equide.color;
            document.getElementById('equideColorText').value = equide.color;
            document.getElementById('equideActive').checked = equide.active;
        } else {
            title.textContent = 'Ajouter un équidé';
            form.reset();
            document.getElementById('equideColor').value = '#8B4513';
            document.getElementById('equideColorText').value = '#8B4513';
            document.getElementById('equideActive').checked = true;
        }
        
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
    }

    openDeleteModal(equide) {
        this.currentEquide = equide;
        
        const modal = document.getElementById('deleteEquideModal');
        document.getElementById('deleteEquideName').textContent = equide.name;
        
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
    }

    // ============= SAUVEGARDE =============
    async saveEquide() {
        const form = document.getElementById('equideForm');
        const formData = new FormData(form);
        
const equideData = {
  name: formData.get('name').trim(),
  type: formData.get('type'),
  // proprietaire_id et owned_by_laury peuvent être ajoutés si vous avez des champs
  actif: formData.get('active') === 'on',
  notes: (formData.get('notes') || '').trim()
};

        
        // Validation
        if (!equideData.name) {
            this.showToast('Le nom est requis', 'error');
            return;
        }
        
        if (!equideData.type) {
            this.showToast('Le type est requis', 'error');
            return;
        }
        
        this.showLoading(true);
        
        try {
            let response;
            if (this.currentEquide) {
                // Modification
                response = await fetch(`/api/equides/${this.currentEquide.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(equideData)
                });
            } else {
                // Ajout
                response = await fetch('/api/equides', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(equideData)
                });
            }
            
            const data = await response.json();
            
            if (response.ok) {
                this.equides = data.equides;
                this.applyFilters();
                this.updateStats();
                this.closeModal('equideModal');
                this.showToast(`Équidé ${this.currentEquide ? 'modifié' : 'ajouté'} avec succès`, 'success');
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

    async deleteEquide() {
        this.showLoading(true);
        
        try {
            const response = await fetch(`/api/equides/${this.currentEquide.id}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.equides = data.equides;
                this.applyFilters();
                this.updateStats();
                this.closeModal('deleteEquideModal');
                this.showToast('Équidé supprimé avec succès', 'success');
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
    editEquide(equide) {
        this.openEquideModal(equide);
    }

    updateColorText() {
        const colorInput = document.getElementById('equideColor');
        const colorText = document.getElementById('equideColorText');
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
        document.getElementById('addEquideBtn').addEventListener('click', () => this.openEquideModal());
        
        // Filtres
        document.getElementById('typeFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('levelFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('activeFilter').addEventListener('change', () => this.applyFilters());
        
        // Formulaire
        document.getElementById('equideForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveEquide();
        });
        
        // Couleur
        document.getElementById('equideColor').addEventListener('input', () => this.updateColorText());
        
        // Modals
        document.getElementById('cancelEquideBtn').addEventListener('click', () => this.closeModal('equideModal'));
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => this.deleteEquide());
        document.getElementById('cancelDeleteBtn').addEventListener('click', () => this.closeModal('deleteEquideModal'));
        
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
                        this.openEquideModal();
                        break;
                }
            }
        });
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    window.equidesManager = new EquidesManager();
});