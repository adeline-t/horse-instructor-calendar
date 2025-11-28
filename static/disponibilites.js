// Gestion des Disponibilités - Script

class DisponibilitesManager {
    constructor() {
        this.disponibilites = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDisponibilites();
    }

    async loadDisponibilites() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/disponibilites');
            const data = await response.json();
            
            if (response.ok) {
                this.disponibilites = data || {};
                this.renderDisponibilites();
            } else {
                this.showToast(`Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors du chargement des disponibilités:', error);
            this.showToast('Erreur lors du chargement des disponibilités', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    bindEvents() {
        document.getElementById('saveDisponibilitesBtn').addEventListener('click', () => {
            this.saveDisponibilites();
        });
    }

    renderDisponibilites() {
        const container = document.getElementById('disponibilitesContainer');
        const jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];
        
        const joursHTML = jours.map(jour => {
            const creneaux = this.disponibilites[jour] || [];
            const creneauxHTML = creneaux.map((creneau, index) => `
                <div class="creneau-item">
                    <input type="time" value="${creneau.start}" data-jour="${jour}" data-index="${index}" data-field="start">
                    <span>à</span>
                    <input type="time" value="${creneau.end}" data-jour="${jour}" data-index="${index}" data-field="end">
                    <input type="text" value="${creneau.label || ''}" placeholder="Libellé" data-jour="${jour}" data-index="${index}" data-field="label">
                    <button class="btn btn-small btn-delete" onclick="disponibilitesManager.removeCreneau('${jour}', ${index})">🗑️</button>
                </div>
            `).join('');
            
            return `
                <div class="jour-disponibilites">
                    <h4>${this.capitalizeFirst(jour)}</h4>
                    <div class="creneaux-list" data-jour="${jour}">
                        ${creneauxHTML}
                    </div>
                    <button class="btn btn-small" onclick="disponibilitesManager.addCreneau('${jour}')">➕ Ajouter un créneau</button>
                </div>
            `;
        }).join('');

        container.innerHTML = joursHTML;
    }

    addCreneau(jour) {
        if (!this.disponibilites[jour]) {
            this.disponibilites[jour] = [];
        }
        
        this.disponibilites[jour].push({
            start: '09:00',
            end: '10:30',
            label: ''
        });
        
        this.renderDisponibilites();
    }

    removeCreneau(jour, index) {
        if (this.disponibilites[jour]) {
            this.disponibilites[jour].splice(index, 1);
            this.renderDisponibilites();
        }
    }

    collectDisponibilites() {
        const jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];
        const nouvellesDisponibilites = {};
        
        jours.forEach(jour => {
            const creneauxElements = document.querySelectorAll(`[data-jour="${jour}"]`);
            const creneaux = [];
            
            // Grouper par index
            const creneauxByIndex = {};
            creneauxElements.forEach(element => {
                const index = element.dataset.index;
                const field = element.dataset.field;
                
                if (!creneauxByIndex[index]) {
                    creneauxByIndex[index] = {};
                }
                creneauxByIndex[index][field] = element.value;
            });
            
            // Convertir en tableau
            Object.values(creneauxByIndex).forEach(creneau => {
                if (creneau.start && creneau.end) {
                    creneaux.push({
                        start: creneau.start,
                        end: creneau.end,
                        label: creneau.label || `${creneau.start} - ${creneau.end}`
                    });
                }
            });
            
            nouvellesDisponibilites[jour] = creneaux;
        });
        
        return nouvellesDisponibilites;
    }

    async saveDisponibilites() {
  const nouvellesDisponibilites = this.collectDisponibilites();
  this.showLoading(true);
  try {
    const response = await fetch('/api/disponibilites', {
      method: 'PUT', // <-- PUT au lieu de POST
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nouvellesDisponibilites)
    });
    const data = await response.json();
    if (response.ok) {
      this.showToast('Disponibilités enregistrées avec succès', 'success');
      this.disponibilites = nouvellesDisponibilites;
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

let disponibilitesManager;

document.addEventListener('DOMContentLoaded', () => {
    disponibilitesManager = new DisponibilitesManager();
});