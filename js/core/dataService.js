/**
 * Data Service Layer for Equestrian Management Application
 * Centralized data operations and API interactions
 */

class DataService {
    constructor() {
        this.baseURL = Utils.APP_CONFIG.API_BASE_URL;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    // Generic CRUD operations
    async getAll(endpoint, useCache = true) {
        const cacheKey = `${endpoint}_all`;
        
        if (useCache && this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const data = await Utils.HttpClient.get(endpoint);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to fetch ${endpoint}`);
            throw error;
        }
    }

    async getById(endpoint, id, useCache = true) {
        const cacheKey = `${endpoint}_${id}`;
        
        if (useCache && this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const data = await Utils.HttpClient.get(`${endpoint}/${id}`);
            this.setCache(cacheKey, data);
            return data;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to fetch ${endpoint} with id ${id}`);
            throw error;
        }
    }

    async create(endpoint, data) {
        try {
            const result = await Utils.HttpClient.post(endpoint, data);
            this.invalidateCache(endpoint);
            return result;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to create ${endpoint}`);
            throw error;
        }
    }

    async update(endpoint, id, data) {
        try {
            const result = await Utils.HttpClient.put(`${endpoint}/${id}`, data);
            this.invalidateCache(endpoint);
            return result;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to update ${endpoint} with id ${id}`);
            throw error;
        }
    }

    async delete(endpoint, id) {
        try {
            const result = await Utils.HttpClient.delete(`${endpoint}/${id}`);
            this.invalidateCache(endpoint);
            return result;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to delete ${endpoint} with id ${id}`);
            throw error;
        }
    }

    // Cache management
    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    isCacheValid(key) {
        const cached = this.cache.get(key);
        if (!cached) return false;
        
        return (Date.now() - cached.timestamp) < this.cacheTimeout;
    }

    invalidateCache(endpoint) {
        // Remove all cache entries for this endpoint
        for (const key of this.cache.keys()) {
            if (key.startsWith(endpoint)) {
                this.cache.delete(key);
            }
        }
    }

    clearCache() {
        this.cache.clear();
    }

    // Specific data service methods
    // Horses/Equines
    async getHorses() {
        return this.getAll('/horses');
    }

    async getHorse(id) {
        return this.getById('/horses', id);
    }

    async createHorse(horseData) {
        return this.create('/horses', horseData);
    }

    async updateHorse(id, horseData) {
        return this.update('/horses', id, horseData);
    }

    async deleteHorse(id) {
        return this.delete('/horses', id);
    }

    async getActiveHorses() {
        const horses = await this.getHorses();
        return horses.filter(horse => horse.actif);
    }

    async getHorsesByOwner(ownerId) {
        const horses = await this.getHorses();
        return horses.filter(horse => horse.proprietaire_id === ownerId);
    }

    // Riders/Cavaliers
    async getRiders() {
        return this.getAll('/riders');
    }

    async getRider(id) {
        return this.getById('/riders', id);
    }

    async createRider(riderData) {
        return this.create('/riders', riderData);
    }

    async updateRider(id, riderData) {
        return this.update('/riders', id, riderData);
    }

    async deleteRider(id) {
        return this.delete('/riders', id);
    }

    async getActiveRiders() {
        const riders = await this.getRiders();
        return riders.filter(rider => rider.actif);
    }

    async getRiderHours(riderId) {
        return this.getById('/riders', `${riderId}/hours`);
    }

    async updateRiderHours(riderId, hoursData) {
        return this.update('/riders', `${riderId}/hours`, hoursData);
    }

    // Recurring Lessons
    async getRecurringLessons() {
        return this.getAll('/recurring-lessons');
    }

    async getRecurringLesson(id) {
        return this.getById('/recurring-lessons', id);
    }

    async createRecurringLesson(lessonData) {
        return this.create('/recurring-lessons', lessonData);
    }

    async updateRecurringLesson(id, lessonData) {
        return this.update('/recurring-lessons', id, lessonData);
    }

    async deleteRecurringLesson(id) {
        return this.delete('/recurring-lessons', id);
    }

    async getActiveRecurringLessons() {
        const lessons = await this.getRecurringLessons();
        return lessons.filter(lesson => lesson.actif);
    }

    async getRecurringLessonsByDay(day) {
        const lessons = await this.getRecurringLessons();
        return lessons.filter(lesson => lesson.jour === day);
    }

    // Availability
    async getAvailability() {
        return this.getAll('/availability');
    }

    async getAvailabilityByDay(day) {
        const availability = await this.getAvailability();
        return availability[day] || [];
    }

    async updateAvailability(day, slots) {
        return this.update('/availability', day, { slots });
    }

    async getAvailableSlots(day) {
        const slots = await this.getAvailabilityByDay(day);
        return slots.filter(slot => !slot.occupied);
    }

    // Schedule/Planning
    async getSchedule(startDate, endDate) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/schedule?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch schedule');
            throw error;
        }
    }

    async createSession(sessionData) {
        try {
            const result = await Utils.HttpClient.post('/schedule', sessionData);
            this.invalidateCache('/schedule');
            return result;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to create session');
            throw error;
        }
    }

    async updateSession(id, sessionData) {
        try {
            const result = await Utils.HttpClient.put(`/schedule/${id}`, sessionData);
            this.invalidateCache('/schedule');
            return result;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to update session');
            throw error;
        }
    }

    async deleteSession(id) {
        try {
            const result = await Utils.HttpClient.delete(`/schedule/${id}`);
            this.invalidateCache('/schedule');
            return result;
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to delete session');
            throw error;
        }
    }

    async getSessionsByDate(date) {
        const schedule = await this.getSchedule(date, date);
        return schedule.filter(session => session.date === date);
    }

    async getSessionsByRider(riderId, startDate, endDate) {
        try {
            const params = new URLSearchParams({
                rider_id: riderId,
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/schedule/rider?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch rider sessions');
            throw error;
        }
    }

    async getSessionsByHorse(horseId, startDate, endDate) {
        try {
            const params = new URLSearchParams({
                horse_id: horseId,
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/schedule/horse?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch horse sessions');
            throw error;
        }
    }

    // Statistics
    async getStatistics(startDate, endDate) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/statistics?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch statistics');
            throw error;
        }
    }

    async getRiderStatistics(riderId, startDate, endDate) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/statistics/riders/${riderId}?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch rider statistics');
            throw error;
        }
    }

    async getHorseStatistics(horseId, startDate, endDate) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/statistics/horses/${horseId}?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch horse statistics');
            throw error;
        }
    }

    async getLessonStatistics(lessonId, startDate, endDate) {
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            return await Utils.HttpClient.get(`/statistics/lessons/${lessonId}?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to fetch lesson statistics');
            throw error;
        }
    }

    // Utility methods
    async validateSession(sessionData) {
        // Check if time slot is available
        const availability = await this.getAvailabilityByDay(sessionData.day);
        const slot = availability.find(s => s.start === sessionData.start_time && s.end === sessionData.end_time);
        
        if (!slot) {
            throw new Error('Time slot not available');
        }

        // Check for conflicts
        const existingSessions = await this.getSessionsByDate(sessionData.date);
        const hasConflict = existingSessions.some(session => {
            return (session.start_time < sessionData.end_time && session.end_time > sessionData.start_time) &&
                   (session.horse_id === sessionData.horse_id || session.rider_id === sessionData.rider_id);
        });

        if (hasConflict) {
            throw new Error('Session conflicts with existing booking');
        }

        return true;
    }

    async generateReport(reportType, filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            return await Utils.HttpClient.get(`/reports/${reportType}?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to generate ${reportType} report`);
            throw error;
        }
    }

    // Search and filtering
    async searchHorses(query) {
        try {
            const params = new URLSearchParams({ q: query });
            return await Utils.HttpClient.get(`/horses/search?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to search horses');
            throw error;
        }
    }

    async searchRiders(query) {
        try {
            const params = new URLSearchParams({ q: query });
            return await Utils.HttpClient.get(`/riders/search?${params}`);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, 'Failed to search riders');
            throw error;
        }
    }

    // Export data
    async exportData(dataType, format = 'json', filters = {}) {
        try {
            const params = new URLSearchParams({ ...filters, format });
            const response = await fetch(`${this.baseURL}/export/${dataType}?${params}`);
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${dataType}_export.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            Utils.ErrorUtils.handleApiError(error, `Failed to export ${dataType}`);
            throw error;
        }
    }
}

// Create singleton instance
const dataService = new DataService();

// Export for global access
window.DataService = dataService;