import React, { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

function App() {
  const [status, setStatus] = useState('checking')
  
  useEffect(() => {
    axios.get(`${API_URL}/`)
      .then(() => setStatus('connected'))
      .catch(() => setStatus('error'))
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui', background: 'linear-gradient(135deg, #1e3a8a, #3b82f6)', color: 'white', minHeight: '100vh' }}>
      <nav style={{ padding: '20px 0', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
            <strong>SIPORTS v2.0</strong>
            <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Accueil</Link>
            <Link to="/exposants" style={{ color: 'white', textDecoration: 'none' }}>Exposants</Link>
            <Link to="/admin" style={{ color: 'white', textDecoration: 'none' }}>Admin</Link>
            <span style={{
              padding: '4px 8px', 
              borderRadius: '4px', 
              fontSize: '12px',
              background: status === 'connected' ? '#059669' : status === 'error' ? '#dc2626' : '#f59e0b'
            }}>
              {status === 'connected' ? '🟢 Backend OK' : status === 'error' ? '🔴 Error' : '🟡 Checking'}
            </span>
          </div>
        </div>
      </nav>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/exposants" element={<ExposantsPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </div>
  )
}

function HomePage() {
  return (
    <div style={{ background: 'rgba(255,255,255,0.1)', padding: '30px', borderRadius: '12px', backdropFilter: 'blur(10px)' }}>
      <h1 style={{ fontSize: '2.5em', marginBottom: '20px' }}>🚢 SIPORTS v2.0</h1>
      <p style={{ fontSize: '1.2em', marginBottom: '30px' }}>
        Plateforme événementielle maritime complète avec backend FastAPI et PostgreSQL
      </p>
      <Link to="/exposants">
        <button style={{
          background: '#10b981',
          color: 'white',
          border: 'none',
          padding: '15px 30px',
          borderRadius: '8px',
          fontSize: '16px',
          cursor: 'pointer'
        }}>
          Découvrir les Exposants
        </button>
      </Link>
    </div>
  )
}

function ExposantsPage() {
  const [exposants, setExposants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    axios.get(`${API_URL}/api/exposants`)
      .then(response => {
        setExposants(response.data.exposants || [])
        setError(null)
      })
      .catch(err => {
        setError(err.message)
        console.error('API Error:', err)
      })
      .finally(() => setLoading(false))
  }, [])
  
  if (loading) {
    return (
      <div style={{ background: 'rgba(255,255,255,0.1)', padding: '20px', borderRadius: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ 
            width: '20px', 
            height: '20px', 
            border: '2px solid rgba(255,255,255,0.3)', 
            borderTop: '2px solid white', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite' 
          }}></div>
          Chargement des exposants...
        </div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div style={{ background: '#dc2626', padding: '20px', borderRadius: '8px' }}>
        <h2>❌ Erreur API</h2>
        <p><strong>Erreur:</strong> {error}</p>
        <p><strong>Backend URL:</strong> {API_URL}</p>
        <small>Vérifiez que le backend Railway est accessible</small>
      </div>
    )
  }
  
  return (
    <div>
      <h1>🏢 Annuaire des Exposants</h1>
      {exposants.length > 0 && (
        <div style={{ background: '#059669', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
          ✅ {exposants.length} exposants trouvés avec succès !
        </div>
      )}
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
        {exposants.map(exposant => (
          <div key={exposant.id} style={{ 
            background: 'rgba(255,255,255,0.1)', 
            padding: '20px', 
            borderRadius: '12px',
            backdropFilter: 'blur(10px)' 
          }}>
            <h3 style={{ color: '#60a5fa', marginBottom: '10px' }}>{exposant.name}</h3>
            <p><strong>Catégorie:</strong> {exposant.category}</p>
            <p><strong>Stand:</strong> {exposant.stand} - {exposant.hall}</p>
            <p style={{ marginTop: '15px' }}>{exposant.description}</p>
            {exposant.specialties && (
              <div style={{ marginTop: '15px' }}>
                <strong>Spécialités:</strong>
                <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                  {exposant.specialties.map((spec, idx) => (
                    <li key={idx}>{spec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, loginForm)
      
      if (response.data.access_token) {
        setIsAuthenticated(true)
        
        // Fetch admin stats
        const statsResponse = await axios.get(`${API_URL}/api/admin/dashboard/stats`, {
          headers: { Authorization: `Bearer ${response.data.access_token}` }
        })
        setStats(statsResponse.data)
      }
    } catch (error) {
      alert('Erreur de connexion: ' + error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
    }
  }
  
  if (!isAuthenticated) {
    return (
      <div>
        <h1>🔐 Connexion Administrateur</h1>
        <div style={{ 
          background: 'rgba(255,255,255,0.1)', 
          padding: '30px', 
          borderRadius: '12px', 
          maxWidth: '400px',
          backdropFilter: 'blur(10px)' 
        }}>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px' }}>Email:</label>
              <input 
                type="email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                placeholder="admin@siportevent.com"
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.1)',
                  color: 'white',
                  fontSize: '16px'
                }}
                required
              />
            </div>
            
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '8px' }}>Mot de passe:</label>
              <input 
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                placeholder="admin123"
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.1)',
                  color: 'white',
                  fontSize: '16px'
                }}
                required
              />
            </div>
            
            <button 
              type="submit" 
              disabled={loading}
              style={{
                width: '100%',
                padding: '15px',
                background: loading ? '#6b7280' : '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
          
          <div style={{ marginTop: '20px', fontSize: '14px', opacity: '0.8' }}>
            <strong>Compte de test:</strong><br />
            Email: admin@siportevent.com<br />
            Mot de passe: admin123
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <h1>📊 Dashboard Administrateur</h1>
      
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '20px', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>👥 Total Utilisateurs</h3>
            <div style={{ fontSize: '2.5em', color: '#60a5fa' }}>{stats.total_users}</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '20px', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>👤 Visiteurs</h3>
            <div style={{ fontSize: '2.5em', color: '#34d399' }}>{stats.visitors}</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '20px', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>🏢 Exposants</h3>
            <div style={{ fontSize: '2.5em', color: '#fbbf24' }}>{stats.exhibitors}</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.1)', padding: '20px', borderRadius: '12px', textAlign: 'center' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>🤝 Partenaires</h3>
            <div style={{ fontSize: '2.5em', color: '#a78bfa' }}>{stats.partners}</div>
          </div>
        </div>
      )}
      
      <button 
        onClick={() => {
          setIsAuthenticated(false)
          setStats(null)
          setLoginForm({ email: '', password: '' })
        }}
        style={{
          background: '#ef4444',
          color: 'white',
          border: 'none',
          padding: '12px 24px',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        Se déconnecter
      </button>
    </div>
  )
}

export default App