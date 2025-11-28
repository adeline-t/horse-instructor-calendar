/**
 * Shared Utilities for Equestrian Management Application
 * Common functions used across all pages
 */

// Application Constants
const APP_CONFIG = {
    API_BASE_URL: 'https://leembory.pythonanywhere.com/api',
    DATE_FORMAT: 'YYYY-MM-DD',
    TIME_FORMAT: 'HH:mm',
    PAGINATION_SIZE: 10,
    MODAL_TIMEOUT: 300,
    ANIMATION_DURATION: 300
};

// Data Validation Utilities
class DataValidator {
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static isValidPhone(phone) {
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }

    static isValidTime(time) {
        const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
        return timeRegex.test(time);
    }

    static isValidDate(date) {
        return !isNaN(Date.parse(date));
    }

    static sanitizeInput(input) {
        return input.trim().replace(/[<>]/g, '');
    }
}

// Date and Time Utilities
class DateUtils {
    static formatDate(date, format = APP_CONFIG.DATE_FORMAT) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day);
    }

    static formatTime(time) {
        const [hours, minutes] = time.split(':');
        return `${hours}:${minutes}`;
    }

    static isDateInPast(date) {
        return new Date(date) < new Date();
    }

    static addDaysToDate(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }

    static getWeekDates(startDate) {
        const dates = [];
        const start = new Date(startDate);
        
        for (let i = 0; i < 7; i++) {
            const date = new Date(start);
            date.setDate(start.getDate() + i);
            dates.push(this.formatDate(date));
        }
        
        return dates;
    }
}

// HTTP Request Utilities
class HttpClient {
    static async get(url) {
        try {
            const response = await fetch(`${APP_CONFIG.API_BASE_URL}${url}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('GET request failed:', error);
            throw error;
        }
    }

    static async post(url, data) {
        try {
            const response = await fetch(`${APP_CONFIG.API_BASE_URL}${url}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('POST request failed:', error);
            throw error;
        }
    }

    static async put(url, data) {
        try {
            const response = await fetch(`${APP_CONFIG.API_BASE_URL}${url}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('PUT request failed:', error);
            throw error;
        }
    }

    static async delete(url) {
        try {
            const response = await fetch(`${APP_CONFIG.API_BASE_URL}${url}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('DELETE request failed:', error);
            throw error;
        }
    }
}

// DOM Manipulation Utilities
class DOMUtils {
    static createElement(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    }

    static showElement(element) {
        if (element) {
            element.style.display = 'block';
            element.classList.remove('hidden');
        }
    }

    static hideElement(element) {
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
        }
    }

    static toggleElement(element) {
        if (element) {
            if (element.style.display === 'none') {
                this.showElement(element);
            } else {
                this.hideElement(element);
            }
        }
    }

    static emptyElement(element) {
        if (element) {
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
        }
    }

    static addClass(element, className) {
        if (element) element.classList.add(className);
    }

    static removeClass(element, className) {
        if (element) element.classList.remove(className);
    }

    static hasClass(element, className) {
        return element ? element.classList.contains(className) : false;
    }
}

// Event Management Utilities
class EventUtils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static addEventListeners(element, events) {
        if (!element) return;
        
        Object.entries(events).forEach(([event, handler]) => {
            element.addEventListener(event, handler);
        });
    }

    static removeEventListeners(element, events) {
        if (!element) return;
        
        Object.entries(events).forEach(([event, handler]) => {
            element.removeEventListener(event, handler);
        });
    }
}

// Storage Utilities
class StorageUtils {
    static setItem(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    }

    static getItem(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Failed to read from localStorage:', error);
            return defaultValue;
        }
    }

    static removeItem(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
        }
    }

    static clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Failed to clear localStorage:', error);
        }
    }
}

// Error Handling Utilities
class ErrorUtils {
    static handleApiError(error, customMessage = '') {
        console.error('API Error:', error);
        
        let message = customMessage || 'An error occurred';
        
        if (error.response) {
            message = `Server error: ${error.response.status}`;
        } else if (error.request) {
            message = 'Network error. Please check your connection.';
        } else {
            message = error.message || message;
        }
        
        this.showError(message);
    }

    static showError(message, duration = 5000) {
        // Create error notification
        const errorDiv = DOMUtils.createElement('div', 'error-notification', message);
        document.body.appendChild(errorDiv);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, duration);
    }

    static showSuccess(message, duration = 3000) {
        // Create success notification
        const successDiv = DOMUtils.createElement('div', 'success-notification', message);
        document.body.appendChild(successDiv);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, duration);
    }

    static logError(error, context = '') {
        const errorInfo = {
            timestamp: new Date().toISOString(),
            context,
            message: error.message,
            stack: error.stack
        };
        
        console.error('Application Error:', errorInfo);
        
        // In production, you might send this to a logging service
        if (APP_CONFIG.ENVIRONMENT === 'production') {
            // Send to error logging service
        }
    }
}

// Number Utilities
class NumberUtils {
    static formatCurrency(amount, currency = 'EUR') {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    static formatNumber(number, decimals = 2) {
        return new Intl.NumberFormat('fr-FR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }

    static roundToDecimals(number, decimals = 2) {
        return Math.round(number * Math.pow(10, decimals)) / Math.pow(10, decimals);
    }

    static isNumber(value) {
        return !isNaN(value) && !isNaN(parseFloat(value));
    }

    static clamp(number, min, max) {
        return Math.min(Math.max(number, min), max);
    }
}

// Array Utilities
class ArrayUtils {
    static unique(array) {
        return [...new Set(array)];
    }

    static groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            groups[group] = groups[group] || [];
            groups[group].push(item);
            return groups;
        }, {});
    }

    static sortBy(array, key, ascending = true) {
        return array.sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];
            
            if (aVal < bVal) return ascending ? -1 : 1;
            if (aVal > bVal) return ascending ? 1 : -1;
            return 0;
        });
    }

    static filterBy(array, key, value) {
        return array.filter(item => item[key] === value);
    }

    static findBy(array, key, value) {
        return array.find(item => item[key] === value);
    }

    static paginate(array, page = 1, pageSize = APP_CONFIG.PAGINATION_SIZE) {
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        return array.slice(startIndex, endIndex);
    }
}

// Export all utilities for global access
window.Utils = {
    DataValidator,
    DateUtils,
    HttpClient,
    DOMUtils,
    EventUtils,
    StorageUtils,
    ErrorUtils,
    NumberUtils,
    ArrayUtils,
    APP_CONFIG
};