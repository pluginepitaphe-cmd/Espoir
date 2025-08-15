// Configuration de base pour les appels API avec debug complet
const FORCE_RAILWAY_BACKEND = 'https://siportevent-production.up.railway.app/api';

const getApiBaseUrl = () => {
  // FORCE l'utilisation du backend Railway  
  console.log('🔗 API Base URL forced to Railway:', FORCE_RAILWAY_BACKEND);
  return FORCE_RAILWAY_BACKEND;
};

const API_BASE_URL = getApiBaseUrl();

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log('🌐 API Request:', url);
    console.log('🌐 Options:', options);
    
    // Récupérer le token d'authentification depuis localStorage
    const token = localStorage.getItem('token');
    console.log('🔑 Token found:', !!token);
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      mode: 'cors',
      ...options,
    }

    console.log('🌐 Final request config:', config);

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      console.log('📤 Sending request to:', url);
      const response = await fetch(url, config);
      
      console.log('📥 Response received:', {
        status: response.status,
        statusText: response.statusText,
        headers: [...response.headers.entries()],
        ok: response.ok
      });
      
      const data = await response.json();
      console.log('📥 Response data:', data);
      
      if (!response.ok) {
        console.error('❌ API Error:', {
          status: response.status,
          data: data
        });
        throw new Error(data.detail || data.error || `HTTP error! status: ${response.status}`)
      }
      
      console.log('✅ API Request successful');
      return data
    } catch (error) {
      console.error('❌ API request failed:', {
        url: url,
        error: error.message,
        stack: error.stack,
        name: error.name
      });
      throw error
    }
  }

  // Dashboard stats avec debug
  async getDashboardStats() {
    console.log('📊 Getting dashboard stats...');
    return this.request('/admin/dashboard/stats')
  }

  // Users management avec debug
  async getPendingUsers(page = 1, perPage = 10) {
    console.log('👥 Getting pending users...');
    return this.request(`/admin/users/pending?page=${page}&per_page=${perPage}`)
  }

  async getUsers(filters = {}) {
    console.log('👥 Getting users with filters:', filters);
    const params = new URLSearchParams()
    
    if (filters.page) params.append('page', filters.page)
    if (filters.perPage) params.append('per_page', filters.perPage)
    if (filters.type) params.append('type', filters.type)
    if (filters.status) params.append('status', filters.status)
    if (filters.search) params.append('search', filters.search)
    
    return this.request(`/admin/users?${params.toString()}`)
  }

  async validateUser(userId, adminEmail = 'admin@siportevent.com') {
    console.log('✅ Validating user:', userId);
    return this.request(`/admin/users/${userId}/validate`, {
      method: 'POST',
      body: { admin_email: adminEmail }
    })
  }

  async rejectUser(userId, reason, comment = '', adminEmail = 'admin@siportevent.com') {
    console.log('❌ Rejecting user:', userId);
    return this.request(`/admin/users/${userId}/reject`, {
      method: 'POST',
      body: {
        raison: reason,
        commentaire: comment,
        admin_email: adminEmail
      }
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient