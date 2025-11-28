/**
 * Validation Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const ValidationUtils = {
        /**
         * Validate email
         */
        isValidEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },

        /**
         * Validate phone number
         */
        isValidPhone(phone) {
            const re = /^[\d\s\-\+\(\)]+$/;
            return phone && phone.length >= 10 && re.test(phone);
        },

        /**
         * Validate date format (YYYY-MM-DD)
         */
        isValidDate(dateString) {
            const re = /^\d{4}-\d{2}-\d{2}$/;
            if (!re.test(dateString)) return false;
            const date = new Date(dateString);
            return !isNaN(date.getTime());
        },

        /**
         * Validate time format (HH:mm)
         */
        isValidTime(timeString) {
            const re = /^([01]\d|2[0-3]):([0-5]\d)$/;
            return re.test(timeString);
        },

        /**
         * Validate required field
         */
        isRequired(value) {
            if (value === null || value === undefined) return false;
            if (typeof value === 'string') return value.trim().length > 0;
            return true;
        },

        /**
         * Validate number range
         */
        isInRange(value, min, max) {
            const num
