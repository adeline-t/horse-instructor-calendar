/**
 * Date and Time Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const DateUtils = {
        /**
         * Format date to string
         */
        formatDate(date, format = 'YYYY-MM-DD') {
            if (!date) return '';

            const d = new Date(date);
            if (isNaN(d.getTime())) return '';

            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');

            switch(format) {
                case 'YYYY-MM-DD':
                    return `${year}-${month}-${day}`;
                case 'DD/MM/YYYY':
                    return `${day}/${month}/${year}`;
                case 'MM/DD/YYYY':
                    return `${month}/${day}/${year}`;
                default:
                    return `${year}-${month}-${day}`;
            }
        },

        /**
         * Format time to string
         */
        formatTime(date, format = 'HH:mm') {
            if (!date) return '';

            const d = new Date(date);
            if (isNaN(d.getTime())) return '';

            const hours = String(d.getHours()).padStart(2, '0');
            const minutes = String(d.getMinutes()).padStart(2, '0');

            if (format === 'HH:mm') {
                return `${hours}:${minutes}`;
            } else if (format === 'h:mm A') {
                const h = d.getHours() % 12 || 12;
                const ampm = d.getHours() >= 12 ? 'PM' : 'AM';
                return `${h}:${minutes} ${ampm}`;
            }

            return `${hours}:${minutes}`;
        },

        /**
         * Format datetime to string
         */
        formatDateTime(date) {
            return `${this.formatDate(date)} ${this.formatTime(date)}`;
        },

        /**
         * Parse ISO date string to date object
         */
        parseISO(isoString) {
            if (!isoString) return null;
            const date = new Date(isoString);
            return isNaN(date.getTime()) ? null : date;
        },

        /**
         * Get date only from ISO string (YYYY-MM-DD)
         */
        parseISODateOnly(isoString) {
            if (!isoString) return null;
            return isoString.split('T')[0];
        },

        /**
         * Get time only from ISO string (HH:mm)
         */
        parseISOTimeOnly(isoString) {
            if (!isoString) return null;
            const timePart = isoString.split('T')[1];
            if (!timePart) return null;
            return timePart.slice(0, 5); // HH:mm
        },

        /**
         * Get current date in YYYY-MM-DD format
         */
        getCurrentDate() {
            return this.formatDate(new Date());
        },

        /**
         * Get current time in HH:mm format
         */
        getCurrentTime() {
            return this.formatTime(new Date());
        },

        /**
         * Add days to a date
         */
        addDays(date, days) {
            const result = new Date(date);
            result.setDate(result.getDate() + days);
            return result;
        },

        /**
         * Get day of week (0 = Sunday, 6 = Saturday)
         */
        getDayOfWeek(date) {
            return new Date(date).getDay();
        },

        /**
         * Get week number
         */
        getWeekNumber(date) {
            const d = new Date(date);
            d.setHours(0, 0, 0, 0);
            d.setDate(d.getDate() + 4 - (d.getDay() || 7));
            const yearStart = new Date(d.getFullYear(), 0, 1);
            return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
        },

        /**
         * Get start of week (Monday)
         */
        getStartOfWeek(date) {
            const d = new Date(date);
            const day = d.getDay();
            const diff = d.getDate() - day + (day === 0 ? -6 : 1);
            return new Date(d.setDate(diff));
        },

        /**
         * Get end of week (Sunday)
         */
        getEndOfWeek(date) {
            const start = this.getStartOfWeek(date);
            return this.addDays(start, 6);
        },

        /**
         * Check if two dates are on the same day
         */
        isSameDay(date1, date2) {
            return this.formatDate(date1) === this.formatDate(date2);
        },

        /**
         * Get day name from date
         */
        getDayName(date, short = false) {
            const days = short
                ? ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                : ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            return days[new Date(date).getDay()];
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.DateUtils = DateUtils;

})(window);
