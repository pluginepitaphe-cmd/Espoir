/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://siportevent-production.up.railway.app',
    REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'https://siportevent-production.up.railway.app',
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://siportevent-production.up.railway.app'
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://siportevent-production.up.railway.app/api/:path*'
      }
    ]
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*'
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET,POST,PUT,DELETE,OPTIONS'
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type,Authorization'
          }
        ]
      }
    ]
  }
}

module.exports = nextConfig