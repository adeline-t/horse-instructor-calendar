/**
 * Application Configuration
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const APP_CONFIG = {
        API_BASE_URL: 'https://leembory.pythonanywhere.com/api',
        APP_NAME: 'Equestrian Management',
        VERSION: '1.0.0',
        DEFAULT_LOCALE: 'en-US',
        DATE_FORMAT: 'YYYY-MM-DD',
        TIME_FORMAT: 'HH:mm'
    };

    // Initialize Utils namespace
    global.Utils = global.Utils || {};
    global.Utils.APP_CONFIG = APP_CONFIG;

})(window);
