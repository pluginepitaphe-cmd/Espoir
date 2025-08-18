import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import axios from 'axios'

// Configuration API
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')
  
  useEffect(() => {
    // Test backend connection
    const checkBackend = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/`)
        setBackendStatus('connected')
        console.log('✅ Backend connected:', response.data)
      } catch (error) {
        setBackendStatus('error')
        console.error('❌ Backend connection failed:', error.message)
      }
    }
    
    checkBackend()
  }, [])

  return (
    <div>
      <nav className="nav">
        <div className="container">
          <ul>
            <li><strong>SIPORTS v2.0</strong></li>
            <li><a href="/">Accueil</a></li>
            <li><a href="/exposants">Exposants</a></li>
            <li><a href="/admin">Admin</a></li>
            <li>
              <span style={{
                padding: '4px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                background: backendStatus === 'connected' ? '#22c55e' : 
                           backendStatus === 'error' ? '#ef4444' : '#f59e0b'
              }}>
                {backendStatus === 'connected' ? '🟢 Backend OK' :
                 backendStatus === 'error' ? '🔴 Backend Error' : '🟡 Checking...'}
              </span>
            </li>
          </ul>
        </div>
      </nav>

      <div className="container">
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
    <div>
      <div className="card">
        <h1>🚢 Bienvenue sur SIPORTS v2.0</h1>
        <p>Plateforme événementielle maritime complète</p>
        <div style={{ marginTop: '20px' }}>
          <button className="btn">Découvrir les exposants</button>
        </div>
      </div>
      
      <div className="grid">
        <div className="card">
          <h3>🏢 Exposants</h3>
          <p>Découvrez les entreprises présentes</p>
        </div>
        <div className="card">
          <h3>📦 Forfaits</h3>
          <p>Choisissez votre formule visiteur</p>
        </div>
        <div className="card">
          <h3>🤖 Chatbot IA</h3>
          <p>Assistant intelligent SIPORTS</p>
        </div>
      </div>
    </div>
  )
}

function ExposantsPage() {
  const [exposants, setExposants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchExposants = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/exposants`)
        setExposants(response.data.exposants || [])
        setError(null)
      } catch (err) {
        setError(err.message)
        console.error('❌ Error fetching exposants:', err)
      } finally {
        setLoading(false)
      }
    }
    
    fetchExposants()
  }, [])
  
  if (loading) {
    return (
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="loading"></div>
          <span>Chargement des exposants...</span>
        </div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="error">
        <strong>Erreur de connexion API :</strong> {error}
        <br />
        <small>Vérifiez que le backend est accessible à : {API_BASE_URL}</small>
      </div>
    )
  }
  
  return (
    <div>
      <h1>🏢 Annuaire des Exposants</h1>
      <div className="success">
        ✅ {exposants.length} exposants trouvés
      </div>
      
      <div className="grid">
        {exposants.map(exposant => (
          <div key={exposant.id} className="card">
            <h3>{exposant.name}</h3>
            <p><strong>Catégorie :</strong> {exposant.category}</p>
            <p><strong>Stand :</strong> {exposant.stand} - {exposant.hall}</p>
            <p>{exposant.description}</p>
            <div style={{ marginTop: '15px' }}>
              <strong>Spécialités :</strong>
              <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                {exposant.specialties?.map((spec, idx) => (
                  <li key={idx}>{spec}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AdminPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, loginForm)
      
      if (response.data.access_token) {
        setIsLoggedIn(true)
        localStorage.setItem('token', response.data.access_token)
        
        // Fetch admin stats
        const statsResponse = await axios.get(`${API_BASE_URL}/api/admin/dashboard/stats`, {
          headers: { Authorization: `Bearer ${response.data.access_token}` }
        })
        setStats(statsResponse.data)
      }
    } catch (error) {
      alert('Erreur de connexion: ' + error.message)
    } finally {
      setLoading(false)
    }
  }
  
  if (!isLoggedIn) {
    return (
      <div>
        <h1>🔐 Connexion Admin</h1>
        <div className="card" style={{ maxWidth: '400px' }}>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '15px' }}>
              <label>Email:</label>
              <input 
                type="email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginTop: '5px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.1)',
                  color: 'white'
                }}
                placeholder="admin@siportevent.com"
              />
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label>Mot de passe:</label>
              <input 
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginTop: '5px',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.1)',
                  color: 'white'
                }}
                placeholder="admin123"
              />
            </div>
            
            <button type="submit" className="btn" disabled={loading} style={{ width: '100%' }}>
              {loading ? <div className="loading"></div> : 'Se connecter'}
            </button>
          </form>
          
          <div style={{ marginTop: '15px', fontSize: '14px', opacity: '0.7' }}>
            <strong>Compte de test :</strong><br />
            Email: admin@siportevent.com<br />
            Mot de passe: admin123
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <h1>📊 Dashboard Admin</h1>
      
      {stats && (
        <div className="grid">
          <div className="card">
            <h3>👥 Utilisateurs Total</h3>
            <div style={{ fontSize: '2em', color: '#0891b2' }}>{stats.total_users}</div>
          </div>
          <div className="card">
            <h3>👤 Visiteurs</h3>
            <div style={{ fontSize: '2em', color: '#22c55e' }}>{stats.visitors}</div>
          </div>
          <div className="card">
            <h3>🏢 Exposants</h3>
            <div style={{ fontSize: '2em', color: '#f59e0b' }}>{stats.exhibitors}</div>
          </div>
          <div className="card">
            <h3>🤝 Partenaires</h3>
            <div style={{ fontSize: '2em', color: '#8b5cf6' }}>{stats.partners}</div>
          </div>
        </div>
      )}
      
      <div style={{ marginTop: '20px' }}>
        <button 
          className="btn" 
          onClick={() => {
            setIsLoggedIn(false)
            localStorage.removeItem('token')
            setStats(null)
          }}
        >
          Se déconnecter
        </button>
      </div>
    </div>
  )
}

export default App