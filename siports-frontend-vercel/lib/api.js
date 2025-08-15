// API Configuration pour SIPORTS v2.0
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
                     process.env.REACT_APP_BACKEND_URL || 
                     'https://siportevent-production.up.railway.app';

// API Helper Functions
export const api = {
  // Base URL
  baseURL: API_BASE_URL,

  // Generic API call
  async call(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API Call failed:', error);
      throw error;
    }
  },

  // Health check
  async health() {
    return this.call('/health');
  },

  // Authentication
  async login(email, password) {
    return this.call('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  },

  async getProfile(token) {
    return this.call('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
  },

  // Packages
  async getVisitorPackages() {
    return this.call('/api/visitor-packages');
  },

  async getPartnerPackages() {
    return this.call('/api/partner-packages');
  },

  // Chatbot
  async chat(message, sessionId = null, contextType = 'general') {
    return this.call('/api/chatbot/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context_type: contextType
      })
    });
  },

  async chatbotHealth() {
    return this.call('/api/chatbot/health');
  },

  // Exhibitors
  async getExhibitorMiniSite(exhibitorId) {
    return this.call(`/api/exhibitor/${exhibitorId}/mini-site`);
  },

  async contactExhibitor(contactData) {
    return this.call('/api/exhibitor/mini-site/contact', {
      method: 'POST',
      body: JSON.stringify(contactData)
    });
  },

  // Admin Dashboard
  async getAdminStats(token) {
    return this.call('/api/admin/dashboard/stats', {
      headers: { Authorization: `Bearer ${token}` }
    });
  },

  // Mobile
  async getMobileConfig() {
    return this.call('/api/mobile/config');
  }
};

// Export default
export default api;