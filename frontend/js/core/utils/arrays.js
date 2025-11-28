/**
 * Array Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const ArrayUtils = {
        /**
         * Remove duplicates from array
         */
        unique(array, key = null) {
            if (!key) {
                return [...new Set(array)];
            }

            const seen = new Set();
            return array.filter(item => {
                const value = item[key];
                if (seen.has(value)) {
                    return false;
                }
                seen.add(value);
                return true;
            });
        },

        /**
         * Sort array by property
         */
        sortBy(array, key, ascending = true) {
            return [...array].sort((a, b) => {
                const aVal = a[key];
                const bVal = b[key];

                if (aVal < bVal) return ascending ? -1 : 1;
                if (aVal > bVal) return ascending ? 1 : -1;
                return 0;
            });
        },

        /**
         * Group array by property
         */
        groupBy(array, key) {
            return array.reduce((result, item) => {
                const group = item[key];
                if (!result[group]) {
                    result[group] = [];
                }
                result[group].push(item);
                return result;
            }, {});
        },

        /**
         * Chunk array into smaller arrays
         */
        chunk(array, size) {
            const chunks = [];
            for (let i = 0; i < array.length; i += size) {
                chunks.push(array.slice(i, i + size));
            }
            return chunks;
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.ArrayUtils = ArrayUtils;

})(window);
