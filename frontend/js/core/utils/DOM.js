/**
 * DOM Utilities
 * Equestrian Management System
 */
(function(global) {
    'use strict';

    const DOMUtils = {
        /**
         * Create element with attributes
         */
        createElement(tag, attributes = {}, content = '') {
            const element = document.createElement(tag);

            Object.keys(attributes).forEach(key => {
                if (key === 'className') {
                    element.className = attributes[key];
                } else if (key === 'dataset') {
                    Object.keys(attributes[key]).forEach(dataKey => {
                        element.dataset[dataKey] = attributes[key][dataKey];
                    });
                } else {
                    element.setAttribute(key, attributes[key]);
                }
            });

            if (content) {
                element.innerHTML = content;
            }

            return element;
        },

        /**
         * Remove all children from element
         */
        clearElement(element) {
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
        },

        /**
         * Show element
         */
        show(element) {
            if (element) element.style.display = '';
        },

        /**
         * Hide element
         */
        hide(element) {
            if (element) element.style.display = 'none';
        },

        /**
         * Toggle element visibility
         */
        toggle(element) {
            if (!element) return;
            element.style.display = element.style.display === 'none' ? '' : 'none';
        }
    };

    global.Utils = global.Utils || {};
    global.Utils.DOMUtils = DOMUtils;

})(window);
