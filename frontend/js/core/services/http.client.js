/**
 * HTTP Client (Fetch wrapper)
 * Depends on: Utils.APP_CONFIG
 */
(function(global){
  'use strict';

  const HttpClient = {
    get baseURL() {
      return global.Utils.APP_CONFIG.API_BASE_URL;
    },

    async get(endpoint, params = {}) {
      try {
        const url = new URL(this.baseURL + endpoint);
        Object.keys(params).forEach(key => {
          const val = params[key];
          if (val !== null && val !== undefined) {
            url.searchParams.append(key, val);
          }
        });

        const resp = await fetch(url.toString(), {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return await resp.json();
      } catch (err) {
        console.error('GET error:', err);
        throw err;
      }
    },

    async post(endpoint, data = {}) {
      try {
        const resp = await fetch(this.baseURL + endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return await resp.json();
      } catch (err) {
        console.error('POST error:', err);
        throw err;
      }
    },

    async put(endpoint, data = {}) {
      try {
        const resp = await fetch(this.baseURL + endpoint, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return await resp.json();
      } catch (err) {
        console.error('PUT error:', err);
        throw err;
      }
    },

    async delete(endpoint) {
      try {
        const resp = await fetch(this.baseURL + endpoint, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return await resp.json();
      } catch (err) {
        console.error('DELETE error:', err);
        throw err;
      }
    }
  };

  // Namespace
  global.Services = global.Services || {};
  global.Services.HttpClient = HttpClient;

})(window);
