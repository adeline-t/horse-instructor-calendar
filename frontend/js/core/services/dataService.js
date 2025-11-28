/**
 * DataService (minimum split)
 * - Single facade exposing all domain methods
 * - Uses Services.HttpClient
 * - Includes normalization helpers
 * Depends on: Utils.DateUtils, Services.HttpClient
 */
(function(global){
  'use strict';

  const Http = global.Services.HttpClient;
  const { DateUtils } = global.Utils;

  // ---------- Normalizers (bridge any legacy French keys) ----------
  const normalizeHorse = (h) => ({
    ...h,
    owner_id: h?.owner_id ?? h?.proprietaire_id ?? null,
    active: h?.active ?? h?.actif ?? true
  });

  const normalizeRider = (r) => ({
    ...r,
    active: r?.active ?? r?.actif ?? true
  });

  const normalizeLesson = (l) => ({
    ...l,
    active: l?.active ?? l?.actif ?? true,
    day: l?.day ?? l?.jour ?? null,
    time: l?.time ?? l?.heure ?? null,
    duration: l?.duration ?? l?.duree ?? null
  });

  const normalizeSession = (s) => ({
    ...s,
    rider_id: s?.rider_id ?? s?.cavalier_id ?? null,
    horse_id: s?.horse_id ?? s?.equide_id ?? null
  });

  // ---------- Helpers ----------
  const parseISODateOnly = (iso) => {
    if (!iso) return null;
    return iso.split('T')[0];
  };
  const parseISOTimeOnly = (iso) => {
    if (!iso) return null;
    const part = iso.split('T')[1];
    return part ? part.slice(0, 5) : null;
  };
  const toMinutes = (hhmm) => {
    const [h, m] = (hhmm || '').split(':').map(Number);
    return (h || 0) * 60 + (m || 0);
  };

  // ---------- Facade ----------
  const DataService = {
    // ============ HORSES ============
    async getHorses() {
      const data = await Http.get('/horses');
      return data.map(normalizeHorse);
    },
    async getHorse(id) {
      return normalizeHorse(await Http.get(`/horses/${id}`));
    },
    async createHorse(payload) {
      return normalizeHorse(await Http.post('/horses', payload));
    },
    async updateHorse(id, payload) {
      return normalizeHorse(await Http.put(`/horses/${id}`, payload));
    },
    async deleteHorse(id) {
      return await Http.delete(`/horses/${id}`);
    },
    async getActiveHorses() {
      const list = await this.getHorses();
      return list.filter(h => h.active);
    },
    async getHorsesByOwner(ownerId) {
      const list = await this.getHorses();
      return list.filter(h => h.owner_id === ownerId);
    },
    async searchHorses(q) {
      return await Http.get('/horses/search', { q });
    },

    // ============ RIDERS ============
    async getRiders() {
      const data = await Http.get('/riders');
      return data.map(normalizeRider);
    },
    async getRider(id) {
      return normalizeRider(await Http.get(`/riders/${id}`));
    },
    async createRider(payload) {
      return normalizeRider(await Http.post('/riders', payload));
    },
    async updateRider(id, payload) {
      return normalizeRider(await Http.put(`/riders/${id}`, payload));
    },
    async deleteRider(id) {
      return await Http.delete(`/riders/${id}`);
    },
    async getActiveRiders() {
      const list = await this.getRiders();
      return list.filter(r => r.active);
    },
    async searchRiders(q) {
      return await Http.get('/riders/search', { q });
    },

    // ============ SCHEDULE ============
    async getSchedule(startDate = null, endDate = null) {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const data = await Http.get('/schedule', params);
      return data.map(normalizeSession);
    },
    async getScheduleItem(id) {
      return normalizeSession(await Http.get(`/schedule/${id}`));
    },
    async createScheduleItem(payload) {
      return normalizeSession(await Http.post('/schedule', payload));
    },
    async updateScheduleItem(id, payload) {
      return normalizeSession(await Http.put(`/schedule/${id}`, payload));
    },
    async deleteScheduleItem(id) {
      return await Http.delete(`/schedule/${id}`);
    },
    async getSessionsByDate(date) {
      const schedule = await this.getSchedule(date, date);
      return schedule.filter(s => parseISODateOnly(s.start_time) === date);
    },
    async getRiderSchedule(riderId, startDate = null, endDate = null) {
      const params = { rider_id: riderId };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const data = await Http.get('/schedule/rider', params);
      return data.map(normalizeSession);
    },
    async getHorseSchedule(horseId, startDate = null, endDate = null) {
      const params = { horse_id: horseId };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const data = await Http.get('/schedule/horse', params);
      return data.map(normalizeSession);
    },

    // ============ RECURRING LESSONS ============
    async getRecurringLessons() {
      const data = await Http.get('/recurring-lessons');
      return data.map(normalizeLesson);
    },
    async getRecurringLesson(id) {
      return normalizeLesson(await Http.get(`/recurring-lessons/${id}`));
    },
    async createRecurringLesson(payload) {
      return normalizeLesson(await Http.post('/recurring-lessons', payload));
    },
    async updateRecurringLesson(id, payload) {
      return normalizeLesson(await Http.put(`/recurring-lessons/${id}`, payload));
    },
    async deleteRecurringLesson(id) {
      return await Http.delete(`/recurring-lessons/${id}`);
    },
    async getActiveRecurringLessons() {
      const list = await this.getRecurringLessons();
      return list.filter(l => l.active);
    },
    async getRecurringLessonsByDay(day) {
      const list = await this.getRecurringLessons();
      return list.filter(l => l.day === day);
    },

    // ============ AVAILABILITY ============
    async getAvailability() {
      // Grouped by day: { monday: [{...}], ... }
      return await Http.get('/availability');
    },
    async getAvailabilityByDay(day) {
      // Returns an array of slots for the day
      return await Http.get(`/availability/${day}`);
    },
    async updateAvailabilityByDay(day, slots) {
      return await Http.put(`/availability/${day}`, { slots });
    },

    // ============ STATISTICS ============
    async getStatistics(startDate = null, endDate = null) {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      return await Http.get('/statistics', params);
    },
    async getRiderStatistics(riderId, startDate = null, endDate = null) {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      return await Http.get(`/statistics/riders/${riderId}`, params);
    },
    async getHorseStatistics(horseId, startDate = null, endDate = null) {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      return await Http.get(`/statistics/horses/${horseId}`, params);
    },
    async getLessonStatistics(lessonId, startDate = null, endDate = null) {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      return await Http.get(`/statistics/lessons/${lessonId}`, params);
    },

    // ============ REPORTS / EXPORT ============
    async getReport(reportType, startDate = null, endDate = null) {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      return await Http.get(`/reports/${reportType}`, params);
    },
    async exportData(dataType, format = 'json') {
      return await Http.get(`/export/${dataType}`, { format });
    },

    // ============ VALIDATION ============
    /**
     * Validate a session against availability and overlaps
     * sessionData: { day, date(YYYY-MM-DD), start_time(HH:mm), end_time(HH:mm), horse_id, rider_id, id? }
     */
    async validateSession(sessionData) {
      // 1) Availability slot exists
      const daySlots = await this.getAvailabilityByDay(sessionData.day);
      const hasSlot = daySlots.some(s => s.start === sessionData.start_time && s.end === sessionData.end_time);
      if (!hasSlot) throw new Error('Time slot not available');

      // 2) Overlaps for same date/resource
      const existing = await this.getSessionsByDate(sessionData.date);
      const sStart = toMinutes(sessionData.start_time);
      const sEnd = toMinutes(sessionData.end_time);

      const conflict = existing.some(e => {
        if (sessionData.id && e.id === sessionData.id) return false; // ignore self on update
        const eStart = toMinutes(parseISOTimeOnly(e.start_time) || '');
        const eEnd = toMinutes(parseISOTimeOnly(e.end_time) || '');
        const overlap = eStart < sEnd && eEnd > sStart;
        const sameResource = (e.horse_id === sessionData.horse_id) || (e.rider_id === sessionData.rider_id);
        return overlap && sameResource;
      });

      if (conflict) throw new Error('Session conflicts with existing booking');
      return true;
    }
  };

  // Export
  global.DataService = DataService;

})(window);
