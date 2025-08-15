import { useState, useEffect } from 'react';
import api from '../lib/api';

export default function Home() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [visitorPackages, setVisitorPackages] = useState([]);
  const [partnerPackages, setPartnerPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Test backend connection
        const status = await api.health();
        setBackendStatus(status);

        // Load packages
        const [visitorPkg, partnerPkg] = await Promise.all([
          api.getVisitorPackages(),
          api.getPartnerPackages()
        ]);
        
        setVisitorPackages(visitorPkg.packages || []);
        setPartnerPackages(partnerPkg.packages || []);
        
      } catch (err) {
        setError(err.message);
        console.error('Failed to load data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-blue-600 font-medium">Connexion au backend SIPORTS...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-red-800 mb-4">Erreur de connexion backend</h1>
          <p className="text-red-600 mb-4">{error}</p>
          <p className="text-sm text-red-500">Backend URL: {api.baseURL}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-3xl mr-3">🚢</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SIPORTS v2.0</h1>
                <p className="text-sm text-gray-500">Plateforme d événements maritimes</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                backendStatus?.status === 'healthy' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {backendStatus?.status === 'healthy' ? '🟢 Backend connecté' : '🟡 Backend dégradé'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Backend Status */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="text-2xl mr-2">🔗</span>
            Statut de connexion Backend
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-sm font-medium text-blue-600">Backend URL</p>
              <p className="text-blue-800 break-all">{api.baseURL}</p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm font-medium text-green-600">Database</p>
              <p className="text-green-800">
                {backendStatus?.checks?.database === 'healthy' ? '✅ PostgreSQL connecté' : '❌ Problème DB'}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded">
              <p className="text-sm font-medium text-purple-600">Chatbot IA</p>
              <p className="text-purple-800">
                {backendStatus?.checks?.chatbot === 'healthy' ? '✅ IA opérationnelle' : '❌ IA indisponible'}
              </p>
            </div>
          </div>
        </div>

        {/* Visitor Packages */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6 flex items-center">
            <span className="text-2xl mr-2">🎫</span>
            Forfaits Visiteurs
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {visitorPackages.map((pkg) => (
              <div key={pkg.id} className={`border rounded-lg p-4 ${pkg.popular ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'}`}>
                <div className="text-center">
                  <h3 className="text-lg font-semibold">{pkg.name}</h3>
                  <div className="text-3xl font-bold text-blue-600 my-2">
                    {pkg.price}€
                  </div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {pkg.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center">
                        <span className="text-green-500 mr-2">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                  {pkg.popular && (
                    <div className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded mt-2">
                      Plus populaire
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Partner Packages */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6 flex items-center">
            <span className="text-2xl mr-2">🏢</span>
            Forfaits Partenaires & Exposants
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {partnerPackages.map((pkg) => (
              <div key={pkg.id} className={`border rounded-lg p-4 ${pkg.popular ? 'border-gold-500 ring-2 ring-yellow-200' : 'border-gray-200'}`}>
                <div className="text-center">
                  <h3 className="text-lg font-semibold">{pkg.name}</h3>
                  <div className="text-3xl font-bold text-green-600 my-2">
                    {pkg.price.toLocaleString()}€
                  </div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {pkg.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center">
                        <span className="text-green-500 mr-2">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                  {pkg.mini_site && (
                    <div className="bg-purple-100 text-purple-800 text-xs font-medium px-2 py-1 rounded mt-2">
                      Mini-site inclus
                    </div>
                  )}
                  {pkg.popular && (
                    <div className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2 py-1 rounded mt-2">
                      Recommandé
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-6 flex items-center">
            <span className="text-2xl mr-2">⚡</span>
            Fonctionnalités SIPORTS v2.0
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="text-center p-4">
              <div className="text-4xl mb-2">🤖</div>
              <h3 className="font-medium mb-2">Chatbot IA</h3>
              <p className="text-sm text-gray-600">Assistant intelligent spécialisé maritime</p>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl mb-2">📊</div>
              <h3 className="font-medium mb-2">Dashboard Admin</h3>
              <p className="text-sm text-gray-600">Analytics et gestion temps réel</p>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl mb-2">🌐</div>
              <h3 className="font-medium mb-2">Mini-sites Exposants</h3>
              <p className="text-sm text-gray-600">Vitrine personnalisée pour chaque exposant</p>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl mb-2">📱</div>
              <h3 className="font-medium mb-2">App Mobile</h3>
              <p className="text-sm text-gray-600">iOS et Android natif</p>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl mb-2">🔐</div>
              <h3 className="font-medium mb-2">Authentification</h3>
              <p className="text-sm text-gray-600">JWT sécurisé multi-rôles</p>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl mb-2">💰</div>
              <h3 className="font-medium mb-2">Système monétisé</h3>
              <p className="text-sm text-gray-600">Forfaits visiteurs et partenaires</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <span className="text-3xl mr-2">🚢</span>
            <span className="text-xl font-bold">SIPORTS v2.0</span>
          </div>
          <p className="text-gray-400">
            Plateforme d événements maritimes avec Intelligence Artificielle
          </p>
          <div className="mt-4 flex items-center justify-center space-x-4 text-sm">
            <span>Backend: {api.baseURL}</span>
            <span>•</span>
            <span>Status: {backendStatus?.status}</span>
            <span>•</span>
            <span>Version: {backendStatus?.version}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}