/**
 * Number and Currency Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const NumberUtils = {
        /**
         * Format number with decimals
         */
        formatNumber(number, decimals = 2) {
            return new Intl.NumberFormat('en-US', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }).format(number);
        },

        /**
         * Format currency
         */
        formatCurrency(amount, currency = 'USD') {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },

        /**
         * Parse string to number
         */
        parseNumber(value) {
            const num = parseFloat(value);
            return isNaN(num) ? 0 : num;
        },

        /**
         * Round to decimal places
         */
        round(value, decimals = 2) {
            return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.NumberUtils = NumberUtils;

})(window);
