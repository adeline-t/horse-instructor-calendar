/**
 * Storage Utilities (LocalStorage)
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const StorageUtils = {
        /**
         * Set item in localStorage
         */
        set(key, value) {
            try {
                const serialized = JSON.stringify(value);
                localStorage.setItem(key, serialized);
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },

        /**
         * Get item from localStorage
         */
        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        /**
         * Remove item from localStorage
         */
        remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        },

        /**
         * Clear all localStorage
         */
        clear() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                console.error('Storage clear error:', error);
                return false;
            }
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.StorageUtils = StorageUtils;

})(window);
