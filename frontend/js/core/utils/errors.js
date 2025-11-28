/**
 * Error Handling Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const ErrorUtils = {
        /**
         * Show error message
         */
        showError(message, duration = 5000) {
            console.error(message);
            // TODO: Integrate with a toast/notification library
            alert(`Error: ${message}`);
        },

        /**
         * Show success message
         */
        showSuccess(message, duration = 3000) {
            console.log(message);
            // TODO: Integrate with a toast/notification library
            alert(`Success: ${message}`);
        },

        /**
         * Handle API error
         */
        handleApiError(error) {
            let message = 'An unexpected error occurred';

            if (error.response) {
                // Server responded with error
                message = error.response.data?.message || error.response.data?.error || message;
            } else if (error.request) {
                // No response received
                message = 'No response from server. Please check your connection.';
            } else if (error.message) {
                // Error in request setup
                message = error.message;
            }

            this.showError(message);
            return message;
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.ErrorUtils = ErrorUtils;

})(window);
