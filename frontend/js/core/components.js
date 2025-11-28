/**
 * Shared Components for Equestrian Management Application
 * Reusable UI components used across all pages
 */

// Modal Component
class Modal {
    constructor(options = {}) {
        this.id = options.id || 'modal-' + Date.now();
        this.title = options.title || '';
        this.content = options.content || '';
        this.size = options.size || 'medium'; // small, medium, large, full
        this.closable = options.closable !== false;
        this.showOnLoad = options.showOnLoad === true; // IMPORTANT: Default false for UX compliance
        this.onClose = options.onClose || null;
        this.onOpen = options.onOpen || null;
        
        this.element = null;
        this.isOpen = false;
        
        this.create();
    }

    create() {
        // Create modal structure
        this.element = Utils.DOMUtils.createElement('div', 'modal', `
            <div class="modal-overlay">
                <div class="modal-content modal-${this.size}">
                    <div class="modal-header">
                        <h3 class="modal-title">${this.title}</h3>
                        ${this.closable ? '<button class="modal-close">&times;</button>' : ''}
                    </div>
                    <div class="modal-body">
                        ${this.content}
                    </div>
                </div>
            </div>
        `);
        
        this.element.id = this.id;
        
        // Add event listeners
        this.attachEvents();
        
        // Add to DOM (hidden by default)
        document.body.appendChild(this.element);
        Utils.DOMUtils.hideElement(this.element);
    }

    attachEvents() {
        if (!this.element) return;
        
        const closeBtn = this.element.querySelector('.modal-close');
        const overlay = this.element.querySelector('.modal-overlay');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.close();
                }
            });
        }
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    open() {
        if (!this.element || this.isOpen) return;
        
        Utils.DOMUtils.showElement(this.element);
        this.isOpen = true;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        if (this.onOpen) {
            this.onOpen();
        }
    }

    close() {
        if (!this.element || !this.isOpen) return;
        
        Utils.DOMUtils.hideElement(this.element);
        this.isOpen = false;
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        if (this.onClose) {
            this.onClose();
        }
    }

    setContent(content) {
        const body = this.element.querySelector('.modal-body');
        if (body) {
            body.innerHTML = content;
        }
    }

    setTitle(title) {
        const titleEl = this.element.querySelector('.modal-title');
        if (titleEl) {
            titleEl.textContent = title;
        }
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

// Form Component
class Form {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.fields = options.fields || [];
        this.onSubmit = options.onSubmit || null;
        this.validateOnSubmit = options.validateOnSubmit !== false;
        this.autoSave = options.autoSave || false;
        
        this.data = {};
        this.errors = {};
        
        this.create();
    }

    create() {
        if (!this.container) return;
        
        // Create form structure
        let formHTML = '<form class="app-form">';
        
        this.fields.forEach(field => {
            formHTML += this.createField(field);
        });
        
        formHTML += `
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Save</button>
                <button type="button" class="btn btn-secondary btn-cancel">Cancel</button>
            </div>
        </form>`;
        
        this.container.innerHTML = formHTML;
        
        // Attach events
        this.attachEvents();
    }

    createField(field) {
        const fieldHTML = `
            <div class="form-group ${field.required ? 'required' : ''}">
                <label for="${field.name}">${field.label}</label>
                ${this.createInput(field)}
                ${field.help ? `<small class="form-help">${field.help}</small>` : ''}
                <div class="form-error" id="${field.name}-error"></div>
            </div>
        `;
        
        return fieldHTML;
    }

    createInput(field) {
        switch (field.type) {
            case 'select':
                const options = field.options.map(opt => 
                    `<option value="${opt.value}">${opt.label}</option>`
                ).join('');
                return `<select id="${field.name}" name="${field.name}">${options}</select>`;
                
            case 'textarea':
                return `<textarea id="${field.name}" name="${field.name}" rows="${field.rows || 4}"></textarea>`;
                
            case 'checkbox':
                return `<input type="checkbox" id="${field.name}" name="${field.name}">`;
                
            case 'date':
                return `<input type="date" id="${field.name}" name="${field.name}">`;
                
            case 'time':
                return `<input type="time" id="${field.name}" name="${field.name}">`;
                
            case 'email':
                return `<input type="email" id="${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}">`;
                
            case 'tel':
                return `<input type="tel" id="${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}">`;
                
            default:
                return `<input type="${field.type || 'text'}" id="${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}">`;
        }
    }

    attachEvents() {
        if (!this.container) return;
        
        const form = this.container.querySelector('form');
        const cancelBtn = this.container.querySelector('.btn-cancel');
        
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSubmit();
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.reset();
            });
        }
        
        // Auto-save if enabled
        if (this.autoSave) {
            form.addEventListener('input', Utils.EventUtils.debounce(() => {
                this.saveToStorage();
            }, 1000));
        }
    }

    handleSubmit() {
        this.collectData();
        
        if (this.validateOnSubmit && !this.validate()) {
            return;
        }
        
        if (this.onSubmit) {
            this.onSubmit(this.data);
        }
    }

    collectData() {
        const form = this.container.querySelector('form');
        const formData = new FormData(form);
        
        this.data = {};
        for (let [key, value] of formData.entries()) {
            this.data[key] = value;
        }
        
        // Handle checkboxes
        this.fields.forEach(field => {
            if (field.type === 'checkbox') {
                const checkbox = form.querySelector(`[name="${field.name}"]`);
                this.data[field.name] = checkbox ? checkbox.checked : false;
            }
        });
    }

    validate() {
        this.errors = {};
        let isValid = true;
        
        this.fields.forEach(field => {
            const value = this.data[field.name];
            const errorEl = document.getElementById(`${field.name}-error`);
            
            // Required validation
            if (field.required && !value) {
                this.errors[field.name] = `${field.label} is required`;
                isValid = false;
            }
            
            // Type validation
            if (value) {
                switch (field.type) {
                    case 'email':
                        if (!Utils.DataValidator.isValidEmail(value)) {
                            this.errors[field.name] = 'Please enter a valid email address';
                            isValid = false;
                        }
                        break;
                        
                    case 'tel':
                        if (!Utils.DataValidator.isValidPhone(value)) {
                            this.errors[field.name] = 'Please enter a valid phone number';
                            isValid = false;
                        }
                        break;
                        
                    case 'date':
                        if (!Utils.DataValidator.isValidDate(value)) {
                            this.errors[field.name] = 'Please enter a valid date';
                            isValid = false;
                        }
                        break;
                        
                    case 'time':
                        if (!Utils.DataValidator.isValidTime(value)) {
                            this.errors[field.name] = 'Please enter a valid time';
                            isValid = false;
                        }
                        break;
                }
            }
            
            // Display error
            if (errorEl) {
                errorEl.textContent = this.errors[field.name] || '';
            }
        });
        
        return isValid;
    }

    setData(data) {
        this.data = data;
        const form = this.container.querySelector('form');
        
        Object.entries(data).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value;
                }
            }
        });
    }

    reset() {
        const form = this.container.querySelector('form');
        if (form) {
            form.reset();
        }
        this.data = {};
        this.errors = {};
        
        // Clear error messages
        this.fields.forEach(field => {
            const errorEl = document.getElementById(`${field.name}-error`);
            if (errorEl) {
                errorEl.textContent = '';
            }
        });
    }

    saveToStorage() {
        const storageKey = `form_${this.container.id}`;
        Utils.StorageUtils.setItem(storageKey, this.data);
    }

    loadFromStorage() {
        const storageKey = `form_${this.container.id}`;
        const savedData = Utils.StorageUtils.getItem(storageKey);
        if (savedData) {
            this.setData(savedData);
        }
    }
}

// Table Component
class Table {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.columns = options.columns || [];
        this.data = options.data || [];
        this.sortable = options.sortable !== false;
        this.paginated = options.paginated || false;
        this.pageSize = options.pageSize || Utils.APP_CONFIG.PAGINATION_SIZE;
        this.onRowClick = options.onRowClick || null;
        this.onSort = options.onSort || null;
        
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        
        this.create();
    }

    create() {
        if (!this.container) return;
        
        let tableHTML = `
            <div class="table-container">
                <table class="app-table">
                    <thead>
                        <tr>
        `;
        
        this.columns.forEach(col => {
            const sortableClass = this.sortable && col.sortable !== false ? 'sortable' : '';
            tableHTML += `<th class="${sortableClass}" data-column="${col.key}">${col.label}</th>`;
        });
        
        tableHTML += `
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
        `;
        
        if (this.paginated) {
            tableHTML += '<div class="table-pagination"></div>';
        }
        
        tableHTML += '</div>';
        
        this.container.innerHTML = tableHTML;
        this.attachEvents();
        this.render();
    }

    attachEvents() {
        if (!this.container) return;
        
        // Sort events
        if (this.sortable) {
            const headers = this.container.querySelectorAll('th.sortable');
            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.dataset.column;
                    this.sort(column);
                });
            });
        }
    }

    sort(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }
        
        if (this.onSort) {
            this.onSort(column, this.sortDirection);
        } else {
            this.data = Utils.ArrayUtils.sortBy(this.data, column, this.sortDirection === 'asc');
        }
        
        this.render();
    }

    render() {
        if (!this.container) return;
        
        const tbody = this.container.querySelector('tbody');
        if (!tbody) return;
        
        // Get data to display
        let displayData = this.data;
        if (this.paginated) {
            displayData = Utils.ArrayUtils.paginate(this.data, this.currentPage, this.pageSize);
        }
        
        // Clear existing rows
        Utils.DOMUtils.emptyElement(tbody);
        
        // Create rows
        displayData.forEach(row => {
            const tr = document.createElement('tr');
            
            this.columns.forEach(col => {
                const td = document.createElement('td');
                td.textContent = this.formatCellValue(row[col.key], col);
                
                if (col.className) {
                    td.className = col.className;
                }
                
                tr.appendChild(td);
            });
            
            // Row click event
            if (this.onRowClick) {
                tr.addEventListener('click', () => {
                    this.onRowClick(row);
                });
                tr.style.cursor = 'pointer';
            }
            
            tbody.appendChild(tr);
        });
        
        // Update pagination
        if (this.paginated) {
            this.renderPagination();
        }
    }

    formatCellValue(value, column) {
        if (column.formatter) {
            return column.formatter(value);
        }
        
        if (value === null || value === undefined) {
            return '-';
        }
        
        return value.toString();
    }

    renderPagination() {
        const paginationContainer = this.container.querySelector('.table-pagination');
        if (!paginationContainer) return;
        
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        
        let paginationHTML = '<div class="pagination">';
        
        // Previous button
        if (this.currentPage > 1) {
            paginationHTML += `<button class="btn btn-sm" onclick="table.previousPage()">Previous</button>`;
        }
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const activeClass = i === this.currentPage ? 'active' : '';
            paginationHTML += `<button class="btn btn-sm ${activeClass}" onclick="table.goToPage(${i})">${i}</button>`;
        }
        
        // Next button
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="btn btn-sm" onclick="table.nextPage()">Next</button>`;
        }
        
        paginationHTML += '</div>';
        
        paginationContainer.innerHTML = paginationHTML;
        
        // Store reference for pagination buttons
        window.table = this;
    }

    setData(data) {
        this.data = data;
        this.currentPage = 1;
        this.render();
    }

    nextPage() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.render();
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.render();
        }
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.render();
        }
    }
}

// Notification Component
class Notification {
    static show(message, type = 'info', duration = 5000) {
        const notification = Utils.DOMUtils.createElement('div', `notification notification-${type}`, message);
        document.body.appendChild(notification);
        
        // Auto-remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
    }

    static success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }

    static error(message, duration = 5000) {
        this.show(message, 'error', duration);
    }

    static warning(message, duration = 4000) {
        this.show(message, 'warning', duration);
    }

    static info(message, duration = 4000) {
        this.show(message, 'info', duration);
    }
}

// Loading Component
class Loading {
    static show(container = null, message = 'Loading...') {
        const loadingElement = Utils.DOMUtils.createElement('div', 'loading-overlay', `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-message">${message}</div>
            </div>
        `);
        
        if (container) {
            const containerEl = typeof container === 'string' ? document.querySelector(container) : container;
            if (containerEl) {
                containerEl.appendChild(loadingElement);
            }
        } else {
            document.body.appendChild(loadingElement);
        }
        
        return loadingElement;
    }

    static hide(loadingElement) {
        if (loadingElement && loadingElement.parentNode) {
            loadingElement.parentNode.removeChild(loadingElement);
        }
    }
}

// Export components for global access
window.Components = {
    Modal,
    Form,
    Table,
    Notification,
    Loading
};