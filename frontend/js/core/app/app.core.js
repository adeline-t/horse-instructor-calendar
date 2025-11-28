/**
 * Equestrian Management - Application Core
 * Minimal split from app.js: class and all methods here
 * Depends on: Utils, Components, DataService
 */
(function(global){
  'use strict';

  class EquestrianApp {
    constructor() {
      this.currentPage = null;
      this.user = null;
      this.config = Utils.APP_CONFIG;
      this.modules = new Map();
      this.eventListeners = new Map();
      this.preferences = null;

      this.init();
    }

    async init() {
      try {
        console.log('Initializing Equestrian Management Application...');
        await this.checkAuth();
        this.loadUserPreferences();
        this.setupGlobalEvents();
        this.setupRouting();
        this.loadInitialPage();
        this.setupErrorHandling();
        console.log('Application initialized successfully');
      } catch (error) {
        console.error('Application initialization failed:', error);
        Utils.ErrorUtils.showError('Failed to initialize application. Please refresh the page.');
      }
    }

    async checkAuth() {
      const token = Utils.StorageUtils.get('auth_token');
      if (token) {
        try {
          this.user = await this.verifyToken(token);
        } catch (error) {
          Utils.StorageUtils.remove('auth_token');
          this.user = null;
        }
      }
      if (!this.user) {
        this.showLoginModal();
      }
    }

    async verifyToken(token) {
      // Simulate token verification
      return {
        id: 1,
        name: 'Admin User',
        email: 'admin@equestrian.com',
        role: 'admin'
      };
    }

    showLoginModal() {
      const loginModal = new Components.Modal({
        title: 'Login',
        content: `
          <form id="login-form">
            <div class="form-group">
              <label for="email">Email</label>
              <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
              <label for="password">Password</label>
              <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
          </form>
        `,
        closable: false
      });

      loginModal.open();

      const loginForm = document.getElementById('login-form');
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(loginForm);
        const credentials = {
          email: formData.get('email'),
          password: formData.get('password')
        };

        try {
          const result = await this.login(credentials);
          Utils.StorageUtils.set('auth_token', result.token);
          this.user = result.user;
          loginModal.close();
          loginModal.destroy();
          Components.Notification.success('Login successful!');
        } catch {
          Utils.ErrorUtils.showError('Invalid credentials');
        }
      });
    }

    async login(credentials) {
      if (credentials.email === 'admin@equestrian.com' && credentials.password === 'password') {
        return {
          token: 'mock-token-' + Date.now(),
          user: {
            id: 1,
            name: 'Admin User',
            email: credentials.email,
            role: 'admin'
          }
        };
      }
      throw new Error('Invalid credentials');
    }

    logout() {
      Utils.StorageUtils.remove('auth_token');
      this.user = null;
      this.navigateTo('login');
    }

    loadUserPreferences() {
      this.preferences = Utils.StorageUtils.get('user_preferences', {
        theme: 'light',
        language: 'en',
        pageSize: 10
      });
      this.applyTheme(this.preferences.theme);
    }

    applyTheme(theme) {
      document.body.className = document.body.className.replace(/theme-\w+/, '');
      document.body.classList.add(`theme-${theme}`);
    }

    setupGlobalEvents() {
      // Navigation events
      document.addEventListener('click', (e) => {
        const el = e.target.closest('[data-nav]');
        if (el) {
          e.preventDefault();
          this.navigateTo(el.dataset.nav);
        }
      });

      // Logout event
      document.addEventListener('click', (e) => {
        const el = e.target.closest('[data-logout]');
        if (el) {
          e.preventDefault();
          this.logout();
        }
      });

      // Theme toggle
      document.addEventListener('click', (e) => {
        const el = e.target.closest('[data-theme-toggle]');
        if (el) {
          e.preventDefault();
          this.toggleTheme();
        }
      });

      // Keyboard shortcuts
      document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
          e.preventDefault();
          this.showGlobalSearch();
        }
        if (e.key === 'Escape') {
          this.closeAllModals();
        }
      });
    }

    setupRouting() {
      window.addEventListener('hashchange', () => this.handleRoute());
      this.handleRoute();
    }

    handleRoute() {
      const hash = window.location.hash.slice(1) || 'dashboard';
      this.navigateTo(hash);
    }

    navigateTo(page) {
      if (this.currentPage === page) return;
      window.location.hash = page;
      this.loadPage(page);
    }

    async loadPage(page) {
      try {
        Components.Loading.show();
        this.updateNavigation(page);
        const content = await this.loadPageContent(page);

        const mainContent = document.getElementById('main-content');
        if (mainContent) {
          mainContent.innerHTML = content;
          this.initializePage(page);
        }

        this.currentPage = page;
      } catch (error) {
        console.error('Failed to load page:', error);
        Utils.ErrorUtils.showError('Failed to load page');
      } finally {
        Components.Loading.hide();
      }
    }

    async loadPageContent(page) {
      const pageMap = {
        dashboard: this.getDashboardContent(),
        horses: this.getHorsesContent(),
        riders: this.getRidersContent(),
        lessons: this.getLessonsContent(),
        availability: this.getAvailabilityContent(),
        schedule: this.getScheduleContent(),
        statistics: this.getStatisticsContent()
      };
      return pageMap[page] || '<h1>Page Not Found</h1>';
    }

    // ------- Pages HTML -------
    getDashboardContent() {
      return `
        <div class="dashboard">
          <h1>Dashboard</h1>
          <div class="dashboard-grid">
            <div class="dashboard-card">
              <h3>Total Horses</h3>
              <div class="dashboard-value" id="total-horses">-</div>
            </div>
            <div class="dashboard-card">
              <h3>Total Riders</h3>
              <div class="dashboard-value" id="total-riders">-</div>
            </div>
            <div class="dashboard-card">
              <h3>This Week's Lessons</h3>
              <div class="dashboard-value" id="week-lessons">-</div>
            </div>
            <div class="dashboard-card">
              <h3>Available Slots Today</h3>
              <div class="dashboard-value" id="today-slots">-</div>
            </div>
          </div>
        </div>
      `;
    }

    getHorsesContent() {
      return `
        <div class="horses-page">
          <div class="page-header">
            <h1>Horses</h1>
            <button class="btn btn-primary" onclick="app.showAddHorseModal()">Add Horse</button>
          </div>
          <div id="horses-table"></div>
        </div>
      `;
    }

    getRidersContent() {
      return `
        <div class="riders-page">
          <div class="page-header">
            <h1>Riders</h1>
            <button class="btn btn-primary" onclick="app.showAddRiderModal()">Add Rider</button>
          </div>
          <div id="riders-table"></div>
        </div>
      `;
    }

    getLessonsContent() {
      return `
        <div class="lessons-page">
          <div class="page-header">
            <h1>Recurring Lessons</h1>
            <button class="btn btn-primary" onclick="app.showAddLessonModal()">Add Lesson</button>
          </div>
          <div id="lessons-table"></div>
        </div>
      `;
    }

    getAvailabilityContent() {
      return `
        <div class="availability-page">
          <div class="page-header">
            <h1>Availability</h1>
            <button class="btn btn-primary" onclick="app.showEditAvailabilityModal()">Edit Availability</button>
          </div>
          <div id="availability-grid"></div>
        </div>
      `;
    }

    getScheduleContent() {
      return `
        <div class="schedule-page">
          <div class="page-header">
            <h1>Schedule</h1>
            <div class="schedule-controls">
              <input type="date" id="schedule-date" class="form-control">
              <button class="btn btn-primary" onclick="app.loadSchedule()">Load Schedule</button>
            </div>
          </div>
          <div id="schedule-calendar"></div>
        </div>
      `;
    }

    getStatisticsContent() {
      return `
        <div class="statistics-page">
          <div class="page-header">
            <h1>Statistics</h1>
            <div class="stats-controls">
              <input type="date" id="stats-start-date" class="form-control">
              <input type="date" id="stats-end-date" class="form-control">
              <button class="btn btn-primary" onclick="app.loadStatistics()">Generate Stats</button>
            </div>
          </div>
          <div id="statistics-content"></div>
        </div>
      `;
    }

    // ------- Page initialization -------
    initializePage(page) {
      switch (page) {
        case 'dashboard':
          this.initializeDashboard();
          break;
        case 'horses':
          this.initializeHorsesPage();
          break;
        case 'riders':
          this.initializeRidersPage();
          break;
        case 'lessons':
          this.initializeLessonsPage();
          break;
        case 'availability':
          this.initializeAvailabilityPage();
          break;
        case 'schedule':
          this.initializeSchedulePage();
          break;
        case 'statistics':
          this.initializeStatisticsPage();
          break;
      }
    }

    async initializeDashboard() {
      try {
        const [horses, riders] = await Promise.all([
          DataService.getHorses(),
          DataService.getRiders()
        ]);
        const horsesEl = document.getElementById('total-horses');
        const ridersEl = document.getElementById('total-riders');
        if (horsesEl) horsesEl.textContent = horses.length;
        if (ridersEl) ridersEl.textContent = riders.length;
        this.loadDashboardStats();
      } catch (error) {
        console.error('Failed to initialize dashboard:', error);
      }
    }

    async loadDashboardStats() {
      try {
        const today = Utils.DateUtils.formatDate(new Date());
        const weekStart = Utils.DateUtils.getStartOfWeek(new Date());
        const weekEnd = Utils.DateUtils.getEndOfWeek(new Date());
        const [weekLessons, todaySlots] = await Promise.all([
          DataService.getSchedule(Utils.DateUtils.formatDate(weekStart), Utils.DateUtils.formatDate(weekEnd)),
          DataService.getAvailabilityByDay(this.getDayName(new Date()))
        ]);

        const weekEl = document.getElementById('week-lessons');
        const slotsEl = document.getElementById('today-slots');
        if (weekEl) weekEl.textContent = weekLessons.length;
        if (slotsEl) slotsEl.textContent = todaySlots.filter(s => !s.occupied).length;
      } catch (error) {
        console.error('Failed to load dashboard stats:', error);
      }
    }

    initializeHorsesPage() {
      const table = new Components.Table('#horses-table', {
        columns: [
          { key: 'name', label: 'Name', sortable: true },
          { key: 'type', label: 'Type' },
          { key: 'owner_id', label: 'Owner ID' },
          { key: 'active', label: 'Active', formatter: (value) => value ? 'Yes' : 'No' },
          { key: 'notes', label: 'Notes' }
        ],
        data: [],
        onRowClick: (horse) => this.showHorseDetails(horse)
      });
      this.loadHorsesData(table);
    }

    async loadHorsesData(table) {
      try {
        const horses = await DataService.getHorses();
        // Normalize just in case backend still sends French keys
        const normalized = horses.map(h => ({
          ...h,
          owner_id: h.owner_id ?? h.proprietaire_id,
          active: h.active ?? h.actif
        }));
        table.setData(normalized);
      } catch (error) {
        Utils.ErrorUtils.showError('Failed to load horses data');
      }
    }

    updateNavigation(activePage) {
      document.querySelectorAll('[data-nav]').forEach(nav => {
        nav.classList.remove('active');
        if (nav.dataset.nav === activePage) {
          nav.classList.add('active');
        }
      });
    }

    setupErrorHandling() {
      window.addEventListener('error', (event) => {
        if (event?.error) {
          Utils.ErrorUtils.showError(event.error.message || 'Unexpected error');
          Utils.ErrorUtils.handleApiError(event.error);
        }
      });
      window.addEventListener('unhandledrejection', (event) => {
        Utils.ErrorUtils.showError(event.reason?.message || 'Unexpected error');
      });
    }

    loadInitialPage() {
      const initialPage = window.location.hash.slice(1) || 'dashboard';
      this.loadPage(initialPage);
    }

    // Utility methods
    getDayName(date) {
      const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
      return days[new Date(date).getDay()];
    }

    toggleTheme() {
      const currentTheme = this.preferences.theme;
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      this.preferences.theme = newTheme;
      Utils.StorageUtils.set('user_preferences', this.preferences);
      this.applyTheme(newTheme);
    }

    showGlobalSearch() {
      console.log('Global search requested');
    }

    closeAllModals() {
      document.querySelectorAll('.modal').forEach(modal => {
        if (modal.style.display !== 'none') {
          modal.style.display = 'none';
        }
      });
    }

    // Placeholder methods for page-specific functionality
    showAddHorseModal() { console.log('Add horse modal'); }
    showAddRiderModal() { console.log('Add rider modal'); }
    showAddLessonModal() { console.log('Add lesson modal'); }
    showEditAvailabilityModal() { console.log('Edit availability modal'); }
    loadSchedule() { console.log('Load schedule'); }
    loadStatistics() { console.log('Load statistics'); }
    initializeRidersPage() { console.log('Initialize riders page'); }
    initializeLessonsPage() { console.log('Initialize lessons page'); }
    initializeAvailabilityPage() { console.log('Initialize availability page'); }
    initializeSchedulePage() { console.log('Initialize schedule page'); }
    initializeStatisticsPage() { console.log('Initialize statistics page'); }
    showHorseDetails(horse) { console.log('Show horse details:', horse); }
  }

  // Export class globally
  global.EquestrianApp = EquestrianApp;

})(window);
