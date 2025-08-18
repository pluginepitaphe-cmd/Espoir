import React, { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

function App() {
  const [status, setStatus] = useState('checking')
  
  useEffect(() => {
    axios.get(`${API_URL}/`)
      .then(() => setStatus('ok'))
      .catch(() => setStatus('error'))
  }, [])

  return (
    <div>
      <nav className="nav">
        <div className="container">
          <ul>
            <li><strong>SIPORTS v2.0</strong></li>
            <li><Link to="/">Accueil</Link></li>
            <li><Link to="/exposants">Exposants</Link></li>
            <li><Link to="/admin">Admin</Link></li>
            <li>
              <span style={{
                padding: '4px 8px', 
                borderRadius: '4px', 
                fontSize: '12px',
                background: status === 'ok' ? '#059669' : status === 'error' ? '#dc2626' : '#f59e0b'
              }}>
                {status === 'ok' ? '🟢 OK' : status === 'error' ? '🔴 Error' : '🟡 Loading'}
              </span>
            </li>
          </ul>
        </div>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/exposants" element={<Exposants />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </div>
    </div>
  )
}

function Home() {
  return (
    <div className="card">
      <h1>🚢 SIPORTS v2.0</h1>
      <p>Plateforme maritime événementielle</p>
      <br />
      <Link to="/exposants">
        <button className="btn">Voir les exposants</button>
      </Link>
    </div>
  )
}

function Exposants() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    axios.get(`${API_URL}/api/exposants`)
      .then(res => setData(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])
  
  if (loading) return <div className="card"><div className="loading"></div> Chargement...</div>
  if (error) return <div className="error">Erreur: {error}</div>
  
  return (
    <div>
      <h1>🏢 Exposants</h1>
      <div className="success">✅ {data?.exposants?.length || 0} exposants trouvés</div>
      {data?.exposants?.map(exp => (
        <div key={exp.id} className="card">
          <h3>{exp.name}</h3>
          <p><strong>{exp.category}</strong> - Stand {exp.stand}</p>
          <p>{exp.description}</p>
        </div>
      ))}
    </div>
  )
}

function Admin() {
  const [auth, setAuth] = useState(false)
  const [form, setForm] = useState({email: '', password: ''})
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  
  const login = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await axios.post(`${API_URL}/api/auth/login`, form)
      if (res.data.access_token) {
        setAuth(true)
        const statsRes = await axios.get(`${API_URL}/api/admin/dashboard/stats`, {
          headers: { Authorization: `Bearer ${res.data.access_token}` }
        })
        setStats(statsRes.data)
      }
    } catch (err) {
      alert('Erreur: ' + err.message)
    }
    setLoading(false)
  }
  
  if (!auth) {
    return (
      <div>
        <h1>🔐 Admin Login</h1>
        <div className="card" style={{maxWidth: '400px'}}>
          <form onSubmit={login}>
            <div style={{marginBottom: '15px'}}>
              <input 
                type="email" 
                placeholder="admin@siportevent.com"
                value={form.email}
                onChange={e => setForm({...form, email: e.target.value})}
                style={{
                  width: '100%', 
                  padding: '10px', 
                  background: 'rgba(255,255,255,0.1)', 
                  border: '1px solid rgba(255,255,255,0.3)', 
                  borderRadius: '4px',
                  color: 'white'
                }}
              />
            </div>
            <div style={{marginBottom: '15px'}}>
              <input 
                type="password" 
                placeholder="admin123"
                value={form.password}
                onChange={e => setForm({...form, password: e.target.value})}
                style={{
                  width: '100%', 
                  padding: '10px', 
                  background: 'rgba(255,255,255,0.1)', 
                  border: '1px solid rgba(255,255,255,0.3)', 
                  borderRadius: '4px',
                  color: 'white'
                }}
              />
            </div>
            <button type="submit" className="btn" disabled={loading} style={{width: '100%'}}>
              {loading ? <div className="loading"></div> : 'Login'}
            </button>
          </form>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <h1>📊 Admin Dashboard</h1>
      {stats && (
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px'}}>
          <div className="card">
            <h3>Total Users</h3>
            <div style={{fontSize: '2em'}}>{stats.total_users}</div>
          </div>
          <div className="card">
            <h3>Visitors</h3>
            <div style={{fontSize: '2em'}}>{stats.visitors}</div>
          </div>
          <div className="card">
            <h3>Exhibitors</h3>
            <div style={{fontSize: '2em'}}>{stats.exhibitors}</div>
          </div>
        </div>
      )}
      <button className="btn" onClick={() => setAuth(false)}>Logout</button>
    </div>
  )
}

export default App