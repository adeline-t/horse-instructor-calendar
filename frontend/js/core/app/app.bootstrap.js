/**
 * Equestrian Management - App Bootstrap
 * Minimal split: starts the app and exposes instance
 * Depends on: EquestrianApp (app.core.js)
 */
(function(global){
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    global.app = new global.EquestrianApp();
  });

})(window);
