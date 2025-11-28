// Gestion des Heures (allocations cavalier ↔ équidé)

class HeuresCavaliersManager {
  constructor() {
    this.cavaliers = [];
    this.equides = [];
    this.allocations = []; // liste [{id,cavalier_id,equide_id,date_debut,date_fin,hours_per_week,notes}]
    this.init();
  }

  init() {
    this.loadDonnees();
  }

  async loadDonnees() {
    this.showLoading(true);
    try {
      const [cavRes, eqRes, allRes] = await Promise.all([
        fetch('/api/cavaliers'),
        fetch('/api/equides'),
        fetch('/api/heures') // <-- API correcte
      ]);
      this.cavaliers = (await cavRes.json()) || [];
      this.equides = (await eqRes.json()) || [];
      // /api/heures retourne soit liste, soit {allocations: [...]}
      const raw = await allRes.json();
      this.allocations = Array.isArray(raw) ? raw : (raw.allocations || []);

      this.renderHeures();
    } catch (e) {
      console.error(e);
      this.showToast('Erreur lors du chargement des données', 'error');
    } finally {
      this.showLoading(false);
    }
  }

  renderHeures() {
    const container = document.getElementById('heuresContainer');
    if (!this.cavaliers || this.cavaliers.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">⏱️</div>
          <h3>Aucun cavalier</h3>
          <p>Ajoutez des cavaliers avant de créer des allocations</p>
        </div>`;
      return;
    }

    // Regrouper les allocations par cavalier
    const byCavalier = {};
    for (const a of this.allocations) {
      byCavalier[a.cavalier_id] = byCavalier[a.cavalier_id] || [];
      byCavalier[a.cavalier_id].push(a);
    }

    const eqMap = Object.fromEntries(this.equides.map(e => [e.id, e]));
    const cavaliersHTML = this.cavaliers.map(cav => {
      const allocs = byCavalier[cav.id] || [];
      const rows = allocs.map(a => {
        const eq = eqMap[a.equide_id];
        return `
          <div class="heure-input" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;">
            <label style="min-width:160px;">${eq ? eq.name : 'Équidé #'+a.equide_id}</label>
            <div class="heure-controls" style="display:flex;align-items:center;gap:6px;">
              <input type="number" min="0" max="168" step="0.5" value="${a.hours_per_week || 0}"
                style="width:90px"
                onchange="heuresManager.updateAllocation(${a.id}, {hours_per_week: parseFloat(this.value)||0})">
              <span>h/sem</span>
            </div>
            <div>
              <label>Du:</label>
              <input type="date" value="${a.date_debut || ''}"
                onchange="heuresManager.updateAllocation(${a.id}, {date_debut: this.value})">
              <label style="margin-left:8px;">Au:</label>
              <input type="date" value="${a.date_fin || ''}"
                onchange="heuresManager.updateAllocation(${a.id}, {date_fin: this.value})">
            </div>
            <button class="btn btn-danger" onclick="heuresManager.deleteAllocation(${a.id})">🗑️</button>
          </div>`;
      }).join('');

      // Ajout d’une nouvelle allocation pour ce cavalier
      const equidesOptions = this.equides
        .filter(e => e.actif !== false)
        .map(e => `<option value="${e.id}">${e.name} (${e.type})</option>`).join('');

      const addForm = `
        <div class="heure-input" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:12px;">
          <select id="new-equide-${cav.id}">
            <option value="">-- Choisir un équidé --</option>
            ${equidesOptions}
          </select>
          <input type="number" id="new-hours-${cav.id}" min="0" max="168" step="0.5" value="1" style="width:90px">
          <span>h/sem</span>
          <label>Du:</label>
          <input type="date" id="new-debut-${cav.id}">
          <label>Au:</label>
          <input type="date" id="new-fin-${cav.id}">
          <button class="btn btn-primary" onclick="heuresManager.createAllocation(${cav.id})">➕ Ajouter</button>
        </div>`;

      const total = allocs.reduce((sum, a) => sum + (parseFloat(a.hours_per_week) || 0), 0);

      return `
        <div class="cavalier-heures">
          <h4>${cav.name}</h4>
          <div class="equides-heures">
            ${rows || '<div style="color:#888;font-style:italic;">Aucune allocation</div>'}
          </div>
          ${addForm}
          <div class="total-heures" style="margin-top:8px;">
            <strong>Total:</strong> <span>${total.toFixed(1)}</span> h/semaine
          </div>
        </div>`;
    }).join('');

    container.innerHTML = cavaliersHTML;
  }

  async createAllocation(cavalierId) {
    const eqSel = document.getElementById(`new-equide-${cavalierId}`);
    const hoursInput = document.getElementById(`new-hours-${cavalierId}`);
    const debutInput = document.getElementById(`new-debut-${cavalierId}`);
    const finInput = document.getElementById(`new-fin-${cavalierId}`);

    const equide_id = parseInt(eqSel.value);
    const hours = parseFloat(hoursInput.value) || 0;
    const date_debut = debutInput.value || '';
    const date_fin = finInput.value || '';

    if (!equide_id) {
      this.showToast('Choisissez un équidé', 'error');
      return;
    }
    if (hours <= 0 || hours > 168) {
      this.showToast('Heures/semaine invalides (0-168)', 'error');
      return;
    }
    if (date_debut && date_fin && date_fin <= date_debut) {
      this.showToast('La date de fin doit être après la date de début', 'error');
      return;
    }

    this.showLoading(true);
    try {
      const res = await fetch('/api/heures', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          cavalier_id: cavalierId,
          equide_id,
          date_debut,
          date_fin,
          hours_per_week: hours
        })
      });
      const data = await res.json();
      if (!res.ok) {
        this.showToast(data.error || 'Erreur création allocation', 'error');
      } else {
        // recharger
        await this.loadDonnees();
        this.showToast('Allocation créée', 'success');
      }
    } catch (e) {
      console.error(e);
      this.showToast('Erreur réseau', 'error');
    } finally {
      this.showLoading(false);
    }
  }

  async updateAllocation(id, patch) {
    // validations légères
    if (patch.date_debut && patch.date_fin && patch.date_fin <= patch.date_debut) {
      this.showToast('La date de fin doit être après la date de début', 'error');
      return;
    }
    if (patch.hours_per_week && (patch.hours_per_week <= 0 || patch.hours_per_week > 168)) {
      this.showToast('Heures/semaine invalides (0-168)', 'error');
      return;
    }

    try {
      const res = await fetch(`/api/heures/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(patch)
      });
      const data = await res.json();
      if (!res.ok) {
        this.showToast(data.error || 'Erreur mise à jour', 'error');
      } else {
        // mettre à jour local
        const idx = this.allocations.findIndex(a => a.id === id);
        if (idx >= 0) this.allocations[idx] = {...this.allocations[idx], ...patch};
        // re-render partiel
        this.renderHeures();
      }
    } catch (e) {
      console.error(e);
      this.showToast('Erreur réseau', 'error');
    }
  }

  async deleteAllocation(id) {
    if (!confirm('Supprimer cette allocation ?')) return;
    this.showLoading(true);
    try {
      const res = await fetch(`/api/heures/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) {
        this.showToast(data.error || 'Erreur suppression', 'error');
      } else {
        this.allocations = this.allocations.filter(a => a.id !== id);
        this.renderHeures();
        this.showToast('Allocation supprimée', 'success');
      }
    } catch (e) {
      console.error(e);
      this.showToast('Erreur réseau', 'error');
    } finally {
      this.showLoading(false);
    }
  }

  showLoading(show) {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) indicator.style.display = show ? 'flex' : 'none';
  }

  showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 3000);
  }
}

let heuresManager;
document.addEventListener('DOMContentLoaded', () => {
  heuresManager = new HeuresCavaliersManager();
});
