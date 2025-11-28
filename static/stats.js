const API_URL = '/api';

document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadStats();

    document.getElementById('filterBtn').addEventListener('click', () => {
        loadStats();
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        document.getElementById('monthFilter').value = '';
        document.getElementById('yearFilter').value = '';
        loadStats();
    });
});

function initializeFilters() {
    const monthFilter = document.getElementById('monthFilter');
    const yearFilter = document.getElementById('yearFilter');

    const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];

    months.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = String(index + 1).padStart(2, '0');
        option.textContent = month;
        monthFilter.appendChild(option);
    });

    const currentYear = new Date().getFullYear();
    for (let year = currentYear - 2; year <= currentYear + 2; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    }

    // Sélectionner le mois et l'année actuels par défaut
    const now = new Date();
    monthFilter.value = String(now.getMonth() + 1).padStart(2, '0');
    yearFilter.value = now.getFullYear();
}

async function loadStats() {
    try {
        const month = document.getElementById('monthFilter').value;
        const year = document.getElementById('yearFilter').value;

        let url = API_URL + '/stats';
        const params = [];
        if (month) params.push('month=' + month);
        if (year) params.push('year=' + year);
        if (params.length > 0) url += '?' + params.join('&');

        const response = await fetch(url);
        const data = await response.json();

        displayCavalierStats(data.cavalier_stats, data.cavaliers_data);
        displayWorkTypeStats(data.work_types);
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}

function displayCavalierStats(stats, cavaliersData) {
    const container = document.getElementById('cavalierStats');
    container.innerHTML = '';

    if (Object.keys(stats).length === 0) {
        container.innerHTML = '<div class="no-stats">Aucune séance enregistrée pour cette période</div>';
        return;
    }

    // Trier par nombre de séances décroissant
    const sorted = Object.entries(stats).sort((a, b) => b[1] - a[1]);

    sorted.forEach(([cavalier, count]) => {
        const item = document.createElement('div');
        item.className = 'stat-item';

        const left = document.createElement('div');
        left.className = 'stat-item-left';

        const cavalierData = cavaliersData.find(c => c.name === cavalier);
        const color = cavalierData ? cavalierData.color : '#667eea';

        const colorDiv = document.createElement('div');
        colorDiv.className = 'stat-color';
        colorDiv.style.backgroundColor = color;

        const name = document.createElement('span');
        name.textContent = cavalier;
        name.style.fontSize = '16px';
        name.style.fontWeight = 'bold';

        left.appendChild(colorDiv);
        left.appendChild(name);

        const countDiv = document.createElement('div');
        countDiv.className = 'stat-count';
        countDiv.textContent = count + ' séance' + (count > 1 ? 's' : '');

        item.appendChild(left);
        item.appendChild(countDiv);
        container.appendChild(item);
    });
}

function displayWorkTypeStats(stats) {
    const container = document.getElementById('workTypeStats');
    container.innerHTML = '';

    if (Object.keys(stats).length === 0) {
        container.innerHTML = '<div class="no-stats">Aucun type de travail enregistré pour cette période</div>';
        return;
    }

    const workTypeIcons = {
        'longe': '🔄',
        'liberte': '🦋',
        'repos': '😴',
        'plat': '🏇',
        'cso': '🚧',
        'balade': '🌳',
        'tap': '🎯'
    };

    const workTypeLabels = {
        'longe': 'Longe',
        'liberte': 'Liberté',
        'repos': 'Repos',
        'plat': 'Plat',
        'cso': 'CSO',
        'balade': 'Balade',
        'tap': 'TAP'
    };

    // Trier par nombre décroissant
    const sorted = Object.entries(stats).sort((a, b) => b[1] - a[1]);

    sorted.forEach(([workType, count]) => {
        const item = document.createElement('div');
        item.className = 'stat-item';

        const left = document.createElement('div');
        left.className = 'stat-item-left';

        const icon = document.createElement('span');
        icon.textContent = workTypeIcons[workType] || '📝';
        icon.style.fontSize = '24px';

        const name = document.createElement('span');
        name.textContent = workTypeLabels[workType] || workType;
        name.style.fontSize = '16px';
        name.style.fontWeight = 'bold';
        name.style.marginLeft = '10px';

        left.appendChild(icon);
        left.appendChild(name);

        const countDiv = document.createElement('div');
        countDiv.className = 'stat-count';
        countDiv.textContent = count + ' séance' + (count > 1 ? 's' : '');

        item.appendChild(left);
        item.appendChild(countDiv);
        container.appendChild(item);
    });
}
