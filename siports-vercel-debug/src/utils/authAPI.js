// Configuration de base pour les appels API d'authentification
import { debugAPI } from './debugAPI.js';

const FORCE_RAILWAY_BACKEND = 'https://siportevent-production.up.railway.app/api';

const getApiBaseUrl = () => {
  // FORCE l'utilisation du backend Railway en production
  console.log('🔗 API Base URL forced to Railway:', FORCE_RAILWAY_BACKEND);
  return FORCE_RAILWAY_BACKEND;
};

const API_BASE_URL = getApiBaseUrl();

// Fonction utilitaire pour faire des appels API d'authentification avec debug
const authApiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('📡 API Call:', url);
  console.log('📡 Options:', options);
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    mode: 'cors',
    ...options,
  };

  console.log('📡 Final config:', config);

  try {
    const response = await fetch(url, config);
    console.log('📡 Response status:', response.status);
    console.log('📡 Response headers:', [...response.headers.entries()]);
    
    const data = await response.json();
    console.log('📡 Response data:', data);
    
    if (!response.ok) {
      console.error('❌ API Error:', data);
      throw new Error(data.detail || data.error || `HTTP ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error('❌ Auth API Error:', error);
    console.error('❌ Full error details:', {
      name: error.name,
      message: error.message,
      stack: error.stack
    });
    
    // Try debug API as fallback
    if (endpoint === '/auth/login' && options.body) {
      console.log('🔄 Trying debug API fallback...');
      const credentials = JSON.parse(options.body);
      const debugResult = await debugAPI.testLogin(credentials.email, credentials.password);
      if (debugResult.success) {
        return debugResult.data;
      }
    }
    
    throw error;
  }
};

// API d'authentification avec debug
export const authAPI = {
  // Connexion avec debug complet
  login: async (email, password) => {
    console.log('🔑 Login attempt:', { email });
    
    try {
      return await authApiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
    } catch (error) {
      console.error('🔑 Login failed:', error);
      throw error;
    }
  },

  // Inscription
  register: async (userData) => {
    console.log('📝 Register attempt:', userData);
    return authApiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Récupérer l'utilisateur connecté
  getCurrentUser: async (token) => {
    return authApiCall('/auth/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  // Connexion visiteur
  visitorLogin: async () => {
    return authApiCall("/auth/visitor-login", {
      method: "POST",
    });
  },
};

export default authAPI;