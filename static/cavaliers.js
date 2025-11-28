const API_URL = '/api';
let editingCavalierId = null;
let allEquides = [];
let allocations = [];

document.addEventListener('DOMContentLoaded', function() {
    loadData();

    const addBtn = document.getElementById('addCavalierBtn');
    if (addBtn) {
        addBtn.addEventListener('click', addCavalier);
    }

    const nameInput = document.getElementById('cavalierName');
    if (nameInput) {
        nameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addCavalier();
            }
        });
    }

    // Modal édition
    const editModal = document.getElementById('editModal');
    const closeEditBtn = document.querySelector('.close-edit');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const saveEditBtn = document.getElementById('saveEditBtn');

    if (closeEditBtn) {
        closeEditBtn.addEventListener('click', () => {
            editModal.style.display = 'none';
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', () => {
            editModal.style.display = 'none';
        });
    }

    if (saveEditBtn) {
        saveEditBtn.addEventListener('click', saveEdit);
    }

    // Modal allocation chevaux
    const allocModal = document.getElementById('allocModal');
    const closeAllocBtn = document.querySelector('.close-alloc');
    const cancelAllocBtn = document.getElementById('cancelAllocBtn');
    const saveAllocBtn = document.getElementById('saveAllocBtn');

    if (closeAllocBtn) {
        closeAllocBtn.addEventListener('click', () => {
            allocModal.style.display = 'none';
        });
    }

    if (cancelAllocBtn) {
        cancelAllocBtn.addEventListener('click', () => {
            allocModal.style.display = 'none';
        });
    }

    if (saveAllocBtn) {
        saveAllocBtn.addEventListener('click', saveAllocations);
    }

    window.addEventListener('click', (e) => {
        if (e.target === editModal) {
            editModal.style.display = 'none';
        }
        if (e.target === allocModal) {
            allocModal.style.display = 'none';
        }
    });
});

async function loadData() {
    try {
        // Charger cavaliers et équidés
        const [cavaliersRes, equidesRes] = await Promise.all([
            fetch(API_URL + '/cavaliers'),
            fetch(API_URL + '/equides')
        ]);

        const cavaliersData = await cavaliersRes.json();
        const equidesData = await equidesRes.json();

        allEquides = equidesData.equides || [];

        // Charger les allocations (essayer différents endpoints)
        try {
            const allocRes = await fetch(API_URL + '/allocations-heures');
            if (allocRes.ok) {
                const allocData = await allocRes.json();
                allocations = allocData.allocations || [];
            } else {
                // Essayer l'autre endpoint
                const allocRes2 = await fetch(API_URL + '/heures/allocations');
                if (allocRes2.ok) {
                    const allocData2 = await allocRes2.json();
                    allocations = allocData2.allocations || [];
                } else {
                    console.warn('Aucun endpoint d\'allocations trouvé');
                    allocations = [];
                }
            }
        } catch (error) {
            console.warn('Erreur lors du chargement des allocations:', error);
            allocations = [];
        }

        displayCavaliers(cavaliersData.cavaliers || []);
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}

function displayCavaliers(cavaliers) {
    const list = document.getElementById('cavaliersList');
    if (!list) return;

    list.innerHTML = '';

    if (cavaliers.length === 0) {
        list.innerHTML = '<li style="text-align: center; color: #999;">Aucun cavalier pour le moment</li>';
        return;
    }

    const today = new Date().toISOString().split('T')[0];

    // Trier: actifs d'abord, puis par nom
    cavaliers.sort((a, b) => {
        if (a.actif !== b.actif) {
            return b.actif ? 1 : -1;
        }
        return a.name.localeCompare(b.name);
    });

    cavaliers.forEach((cavalier) => {
        const li = document.createElement('li');
        li.className = cavalier.actif ? '' : 'cavalier-inactive';

        // Info principale
        const mainInfo = document.createElement('div');
        mainInfo.className = 'cavalier-main-info';

        const info = document.createElement('div');
        info.className = 'cavalier-info';

        const name = document.createElement('span');
        name.textContent = cavalier.name;
        name.style.fontWeight = 'bold';
        name.style.fontSize = '16px';
        if (!cavalier.actif) {
            name.style.textDecoration = 'line-through';
            name.style.opacity = '0.6';
        }

        // Statut
        const status = getCavalierStatus(cavalier, today);
        const statusBadge = document.createElement('span');
        statusBadge.className = 'cavalier-status status-' + status.class;
        statusBadge.textContent = status.text;

        info.appendChild(name);
        info.appendChild(statusBadge);

        // Actions
        const actions = document.createElement('div');
        actions.className = 'cavalier-actions';

        const allocBtn = document.createElement('button');
        allocBtn.className = 'alloc-btn';
        allocBtn.textContent = '🐎 Chevaux';
        allocBtn.addEventListener('click', () => openAllocModal(cavalier));

        const editBtn = document.createElement('button');
        editBtn.className = 'edit-btn';
        editBtn.textContent = '✏️ Modifier';
        editBtn.addEventListener('click', () => openEditModal(cavalier));

        const toggleBtn = document.createElement('button');
        toggleBtn.className = cavalier.actif ? 'toggle-btn' : 'toggle-btn active-btn';
        toggleBtn.textContent = cavalier.actif ? '🔴 Désactiver' : '🟢 Activer';
        toggleBtn.addEventListener('click', () => toggleCavalierStatus(cavalier.id, !cavalier.actif));

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = '🗑️ Supprimer';
        deleteBtn.addEventListener('click', () => deleteCavalier(cavalier.id, cavalier.name));

        actions.appendChild(allocBtn);
        actions.appendChild(editBtn);
        actions.appendChild(toggleBtn);
        actions.appendChild(deleteBtn);

        mainInfo.appendChild(info);
        mainInfo.appendChild(actions);

        // Détails du cavalier
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'cavalier-details';

        // Contact
        if (cavalier.email || cavalier.phone) {
            const contactDiv = document.createElement('div');
            contactDiv.className = 'cavalier-detail-row';

            if (cavalier.email) {
                const emailSpan = document.createElement('span');
                emailSpan.innerHTML = `📧 ${cavalier.email}`;
                contactDiv.appendChild(emailSpan);
            }

            if (cavalier.phone) {
                const phoneSpan = document.createElement('span');
                phoneSpan.innerHTML = `📞 ${cavalier.phone}`;
                contactDiv.appendChild(phoneSpan);
            }

            detailsDiv.appendChild(contactDiv);
        }

        // Heures
        const heuresDiv = document.createElement('div');
        heuresDiv.className = 'cavalier-detail-row';

        const forfaitSpan = document.createElement('span');
        forfaitSpan.innerHTML = `🎫 Forfait CO: <strong>${cavalier.heures_forfait_co || 0}h</strong>`;
        heuresDiv.appendChild(forfaitSpan);

        const partSpan = document.createElement('span');
        partSpan.innerHTML = `👤 Cours part.: <strong>${cavalier.heures_cours_part || 0}h</strong>`;
        heuresDiv.appendChild(partSpan);

        detailsDiv.appendChild(heuresDiv);

        // Chevaux alloués
        if (allocations.length > 0) {
            const cavalierAllocations = allocations.filter(a => a.cavalier_id === cavalier.id && isAllocationActive(a, today));
            if (cavalierAllocations.length > 0) {
                const chevauxDiv = document.createElement('div');
                chevauxDiv.className = 'cavalier-chevaux';
                chevauxDiv.innerHTML = '🐎 <strong>Chevaux alloués:</strong> ';

                const chevauxList = cavalierAllocations.map(alloc => {
                    const equide = allEquides.find(e => e.id === alloc.equide_id);
                    if (equide) {
                        let dateInfo = '';
                        if (alloc.date_debut || alloc.date_fin) {
                            const dates = [];
                            if (alloc.date_debut) dates.push(`du ${formatDateShort(alloc.date_debut)}`);
                            if (alloc.date_fin) dates.push(`au ${formatDateShort(alloc.date_fin)}`);
                            dateInfo = ` <span class="date-range">(${dates.join(' ')})</span>`;
                        }
                        return `<span class="equide-tag" style="background-color: ${equide.color || '#667eea'}22; border-left: 3px solid ${equide.color || '#667eea'};">${equide.name}${dateInfo}</span>`;
                    }
                    return '';
                }).filter(Boolean).join('');

                chevauxDiv.innerHTML += chevauxList;
                detailsDiv.appendChild(chevauxDiv);
            }
        }

        // Dates
        if (cavalier.date_debut || cavalier.date_fin) {
            const datesDiv = document.createElement('div');
            datesDiv.className = 'cavalier-detail-row';

            if (cavalier.date_debut) {
                const startSpan = document.createElement('span');
                startSpan.innerHTML = `📅 Début: ${formatDate(cavalier.date_debut)}`;
                datesDiv.appendChild(startSpan);
            }

            if (cavalier.date_fin) {
                const endSpan = document.createElement('span');
                endSpan.innerHTML = `🏁 Fin: ${formatDate(cavalier.date_fin)}`;
                datesDiv.appendChild(endSpan);
            }

            detailsDiv.appendChild(datesDiv);
        }

        // Notes
        if (cavalier.notes && cavalier.notes.trim()) {
            const notesDiv = document.createElement('div');
            notesDiv.className = 'cavalier-notes';
            notesDiv.innerHTML = `📝 ${cavalier.notes}`;
            detailsDiv.appendChild(notesDiv);
        }

        li.appendChild(mainInfo);
        li.appendChild(detailsDiv);
        list.appendChild(li);
    });
}

function isAllocationActive(allocation, today) {
    if (allocation.date_debut && today < allocation.date_debut) {
        return false;
    }
    if (allocation.date_fin && today > allocation.date_fin) {
        return false;
    }
    return true;
}

function getCavalierStatus(cavalier, today) {
    if (!cavalier.actif) {
        return { class: 'inactive', text: 'Inactif' };
    }

    const startDate = cavalier.date_debut;
    const endDate = cavalier.date_fin;

    if (!startDate && !endDate) {
        return { class: 'active', text: 'Actif' };
    }

    if (endDate && today > endDate) {
        return { class: 'ended', text: 'Terminé' };
    }

    if (startDate && today < startDate) {
        return { class: 'upcoming', text: 'À venir' };
    }

    return { class: 'active', text: 'Actif' };
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
}

function formatDateShort(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function openAllocModal(cavalier) {
    editingCavalierId = cavalier.id;
    document.getElementById('allocCavalierName').textContent = cavalier.name;

    // Récupérer les allocations actuelles du cavalier
    const cavalierAllocations = allocations.filter(a => a.cavalier_id === cavalier.id);

    // Afficher la liste des équidés avec checkboxes
    const equidesList = document.getElementById('allocEquidesList');
    equidesList.innerHTML = '';

    const activeEquides = allEquides.filter(e => e.actif);

    if (activeEquides.length === 0) {
        equidesList.innerHTML = '<p style="text-align: center; color: #999;">Aucun cheval disponible</p>';
    } else {
        activeEquides.forEach(equide => {
            const allocation = cavalierAllocations.find(a => a.equide_id === equide.id);

            const allocItem = document.createElement('div');
            allocItem.className = 'alloc-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `equide_${equide.id}`;
            checkbox.checked = !!allocation;
            checkbox.dataset.equideId = equide.id;
            checkbox.dataset.allocationId = allocation ? allocation.id : '';

            const label = document.createElement('label');
            label.htmlFor = `equide_${equide.id}`;

            const colorIndicator = document.createElement('span');
            colorIndicator.className = 'color-indicator';
            colorIndicator.style.backgroundColor = equide.color || '#667eea';

            const name = document.createElement('span');
            name.textContent = equide.name;

            label.appendChild(colorIndicator);
            label.appendChild(name);

            // Dates de l'allocation
            const datesDiv = document.createElement('div');
            datesDiv.className = 'alloc-dates';
            datesDiv.id = `dates_${equide.id}`;
            datesDiv.style.display = checkbox.checked ? 'block' : 'none';

            const dateDebutInput = document.createElement('input');
            dateDebutInput.type = 'date';
            dateDebutInput.className = 'alloc-date-input';
            dateDebutInput.placeholder = 'Date début';
            dateDebutInput.value = allocation ? (allocation.date_debut || '') : '';
            dateDebutInput.dataset.equideId = equide.id;
            dateDebutInput.dataset.type = 'debut';

            const dateFinInput = document.createElement('input');
            dateFinInput.type = 'date';
            dateFinInput.className = 'alloc-date-input';
            dateFinInput.placeholder = 'Date fin';
            dateFinInput.value = allocation ? (allocation.date_fin || '') : '';
            dateFinInput.dataset.equideId = equide.id;
            dateFinInput.dataset.type = 'fin';

            const dateLabel1 = document.createElement('label');
            dateLabel1.textContent = 'Du:';
            dateLabel1.style.fontSize = '12px';
            dateLabel1.style.marginRight = '5px';

            const dateLabel2 = document.createElement('label');
            dateLabel2.textContent = 'Au:';
            dateLabel2.style.fontSize = '12px';
            dateLabel2.style.marginLeft = '10px';
            dateLabel2.style.marginRight = '5px';

            datesDiv.appendChild(dateLabel1);
            datesDiv.appendChild(dateDebutInput);
            datesDiv.appendChild(dateLabel2);
            datesDiv.appendChild(dateFinInput);

            // Toggle dates visibility
            checkbox.addEventListener('change', () => {
                datesDiv.style.display = checkbox.checked ? 'block' : 'none';
            });

            allocItem.appendChild(checkbox);
            allocItem.appendChild(label);
            allocItem.appendChild(datesDiv);

            equidesList.appendChild(allocItem);
        });
    }

    document.getElementById('allocModal').style.display = 'block';
}

async function saveAllocations() {
    try {
        const equidesList = document.getElementById('allocEquidesList');
        const checkboxes = equidesList.querySelectorAll('input[type="checkbox"]');

        const updates = [];

        for (const checkbox of checkboxes) {
            const equideId = parseInt(checkbox.dataset.equideId);
            const allocationId = checkbox.dataset.allocationId;
            const isChecked = checkbox.checked;

            const dateDebutInput = equidesList.querySelector(`input[data-equide-id="${equideId}"][data-type="debut"]`);
            const dateFinInput = equidesList.querySelector(`input[data-equide-id="${equideId}"][data-type="fin"]`);

            const dateDebut = dateDebutInput ? dateDebutInput.value : '';
            const dateFin = dateFinInput ? dateFinInput.value : '';

            // Validation des dates
            if (dateDebut && dateFin && dateDebut > dateFin) {
                const equide = allEquides.find(e => e.id === equideId);
                alert(`Erreur pour ${equide.name}: la date de fin doit être après la date de début`);
                return;
            }

            if (isChecked) {
                // Créer ou mettre à jour l'allocation
                if (allocationId) {
                    // Mettre à jour
                    updates.push({
                        action: 'update',
                        id: parseInt(allocationId),
                        data: {
                            date_debut: dateDebut || '',
                            date_fin: dateFin || ''
                        }
                    });
                } else {
                    // Créer
                    updates.push({
                        action: 'create',
                        data: {
                            cavalier_id: editingCavalierId,
                            equide_id: equideId,
                            date_debut: dateDebut || '',
                            date_fin: dateFin || ''
                        }
                    });
                }
            } else if (allocationId) {
                // Supprimer l'allocation
                updates.push({
                    action: 'delete',
                    id: parseInt(allocationId)
                });
            }
        }

        // Appliquer les changements
        for (const update of updates) {
            let response;

            if (update.action === 'create') {
                response = await fetch(API_URL + '/heures-allocations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(update.data)
                });
            } else if (update.action === 'update') {
                response = await fetch(API_URL + '/heures-allocations/' + update.id, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(update.data)
                });
            } else if (update.action === 'delete') {
                response = await fetch(API_URL + '/heures-allocations/' + update.id, {
                    method: 'DELETE'
                });
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erreur lors de la mise à jour');
            }
        }

        document.getElementById('allocModal').style.display = 'none';
        await loadData();

    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur: ' + error.message);
    }
}

function openEditModal(cavalier) {
    editingCavalierId = cavalier.id;
    document.getElementById('editCavalierName').textContent = cavalier.name;
    document.getElementById('editName').value = cavalier.name;
    document.getElementById('editEmail').value = cavalier.email || '';
    document.getElementById('editPhone').value = cavalier.phone || '';
    document.getElementById('editHeuresForfait').value = cavalier.heures_forfait_co || 0;
    document.getElementById('editHeuresPart').value = cavalier.heures_cours_part || 0;
    document.getElementById('editStartDate').value = cavalier.date_debut || '';
    document.getElementById('editEndDate').value = cavalier.date_fin || '';
    document.getElementById('editNotes').value = cavalier.notes || '';
    document.getElementById('editModal').style.display = 'block';
}

async function saveEdit() {
    try {
        const name = document.getElementById('editName').value.trim();
        const email = document.getElementById('editEmail').value.trim();
        const phone = document.getElementById('editPhone').value.trim();
        const heuresForfait = parseFloat(document.getElementById('editHeuresForfait').value) || 0;
        const heuresPart = parseFloat(document.getElementById('editHeuresPart').value) || 0;
        const startDate = document.getElementById('editStartDate').value;
        const endDate = document.getElementById('editEndDate').value;
        const notes = document.getElementById('editNotes').value.trim();

        if (!name) {
            alert('Le nom est requis');
            return;
        }

        if (heuresForfait < 0 || heuresPart < 0) {
            alert('Les heures ne peuvent pas être négatives');
            return;
        }

        if (startDate && endDate && startDate > endDate) {
            alert('La date de fin doit être après la date de début');
            return;
        }

        const response = await fetch(API_URL + '/cavaliers/' + editingCavalierId, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email || '',
                phone: phone || '',
                heures_forfait_co: heuresForfait,
                heures_cours_part: heuresPart,
                date_debut: startDate || '',
                date_fin: endDate || '',
                notes: notes || ''
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            document.getElementById('editModal').style.display = 'none';
            loadData();
        } else {
            alert(data.error || 'Erreur lors de la mise à jour');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}

async function addCavalier() {
    const nameInput = document.getElementById('cavalierName');
    const emailInput = document.getElementById('cavalierEmail');
    const phoneInput = document.getElementById('cavalierPhone');
    const heuresForfaitInput = document.getElementById('cavalierHeuresForfait');
    const heuresPartInput = document.getElementById('cavalierHeuresPart');
    const startDateInput = document.getElementById('cavalierStartDate');
    const endDateInput = document.getElementById('cavalierEndDate');
    const notesInput = document.getElementById('cavalierNotes');

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const phone = phoneInput.value.trim();
    const heuresForfait = parseFloat(heuresForfaitInput.value) || 0;
    const heuresPart = parseFloat(heuresPartInput.value) || 0;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    const notes = notesInput.value.trim();

    if (!name) {
        alert('Veuillez entrer un nom');
        return;
    }

    if (heuresForfait < 0 || heuresPart < 0) {
        alert('Les heures ne peuvent pas être négatives');
        return;
    }

    if (startDate && endDate && startDate > endDate) {
        alert('La date de fin doit être après la date de début');
        return;
    }

    try {
        const response = await fetch(API_URL + '/cavaliers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email || '',
                phone: phone || '',
                heures_forfait_co: heuresForfait,
                heures_cours_part: heuresPart,
                date_debut: startDate || '',
                date_fin: endDate || '',
                actif: true,
                notes: notes || ''
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            nameInput.value = '';
            emailInput.value = '';
            phoneInput.value = '';
            heuresForfaitInput.value = '1';
            heuresPartInput.value = '0';
            startDateInput.value = '';
            endDateInput.value = '';
            notesInput.value = '';

            loadData();
        } else {
            alert(data.error || 'Erreur lors de l\'ajout');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}

async function toggleCavalierStatus(cavalier_id, newStatus) {
    const action = newStatus ? 'activer' : 'désactiver';

    if (!confirm(`Voulez-vous vraiment ${action} ce cavalier ?`)) {
        return;
    }

    try {
        const response = await fetch(API_URL + '/cavaliers/' + cavalier_id, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                actif: newStatus
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            loadData();
        } else {
            alert(data.error || 'Erreur lors de la mise à jour du statut');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}

async function deleteCavalier(cavalier_id, cavalier_name) {
    if (!confirm(`Voulez-vous vraiment supprimer définitivement "${cavalier_name}" ?\n\n⚠️ Cette action est irréversible !`)) {
        return;
    }

    try {
        const response = await fetch(API_URL + '/cavaliers/' + cavalier_id, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            loadData();
        } else {
            alert(data.error || 'Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}
