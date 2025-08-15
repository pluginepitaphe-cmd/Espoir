// API de Debug pour diagnostiquer les problèmes de connexion
const RAILWAY_BACKEND = 'https://siportevent-production.up.railway.app/api';

export const debugAPI = {
  // Test de connectivité de base
  async testConnection() {
    console.log('🔍 Testing backend connection...');
    console.log('Backend URL:', RAILWAY_BACKEND);
    
    try {
      const response = await fetch(RAILWAY_BACKEND.replace('/api', '/'), {
        method: 'GET',
        mode: 'cors',
      });
      
      console.log('✅ Backend response status:', response.status);
      console.log('✅ Backend response headers:', [...response.headers.entries()]);
      
      const data = await response.json();
      console.log('✅ Backend response data:', data);
      return { success: true, data };
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      return { success: false, error: error.message };
    }
  },

  // Test d'authentification avec debug complet
  async testLogin(email, password) {
    console.log('🔑 Testing login...');
    console.log('Login URL:', `${RAILWAY_BACKEND}/auth/login`);
    console.log('Credentials:', { email, password });
    
    try {
      const response = await fetch(`${RAILWAY_BACKEND}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        body: JSON.stringify({ email, password }),
      });
      
      console.log('🔑 Login response status:', response.status);
      console.log('🔑 Login response headers:', [...response.headers.entries()]);
      
      if (!response.ok) {
        console.error('❌ Login failed - HTTP status:', response.status);
      }
      
      const data = await response.json();
      console.log('🔑 Login response data:', data);
      
      if (data.access_token) {
        console.log('✅ Login successful! Token received');
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
      }
      
      return { success: true, data };
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      return { success: false, error: error.message };
    }
  },

  // Test des headers CORS
  async testCORS() {
    console.log('🌐 Testing CORS...');
    
    try {
      const response = await fetch(`${RAILWAY_BACKEND}/auth/login`, {
        method: 'OPTIONS',
        headers: {
          'Origin': window.location.origin,
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type',
        },
      });
      
      console.log('🌐 CORS preflight status:', response.status);
      console.log('🌐 CORS headers:', [...response.headers.entries()]);
      
      return { success: response.ok };
    } catch (error) {
      console.error('❌ CORS test failed:', error);
      return { success: false, error: error.message };
    }
  },

  // Diagnostic complet
  async runFullDiagnostic() {
    console.log('🚀 Running full diagnostic...');
    console.log('Current URL:', window.location.href);
    console.log('Origin:', window.location.origin);
    
    const results = {
      connection: await this.testConnection(),
      cors: await this.testCORS(),
      login: await this.testLogin('admin@siportevent.com', 'admin123')
    };
    
    console.log('📊 Diagnostic Results:', results);
    return results;
  }
};

// Auto-run diagnostic on import (for immediate debugging)
if (typeof window !== 'undefined') {
  window.debugAPI = debugAPI;
  console.log('🔧 Debug API loaded. Run debugAPI.runFullDiagnostic() in console');
}