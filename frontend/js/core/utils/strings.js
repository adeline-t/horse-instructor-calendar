/**
 * String Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const StringUtils = {
        /**
         * Capitalize first letter
         */
        capitalize(str) {
            if (!str) return '';
            return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
        },

        /**
         * Capitalize all words
         */
        capitalizeWords(str) {
            if (!str) return '';
            return str.split(' ').map(word => this.capitalize(word)).join(' ');
        },

        /**
         * Truncate string
         */
        truncate(str, maxLength, suffix = '...') {
            if (!str || str.length <= maxLength) return str;
            return str.substring(0, maxLength) + suffix;
        },

        /**
         * Remove special characters
         */
        sanitize(str) {
            if (!str) return '';
            return str.replace(/[^a-zA-Z0-9\s-]/g, '');
        },

        /**
         * Generate slug from string
         */
        slugify(str) {
            if (!str) return '';
            return str
                .toLowerCase()
                .replace(/\s+/g, '-')
                .replace(/[^\w-]+/g, '')
                .replace(/--+/g, '-')
                .trim();
        },

        /**
         * Check if string is empty
         */
        isEmpty(str) {
            return !str || str.trim().length === 0;
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.StringUtils = StringUtils;

})(window);
