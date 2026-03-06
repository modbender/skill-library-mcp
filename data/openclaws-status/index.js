const express = require('express')
const axios = require('axios')

const app = express()
app.use(express.json())

const PAYTO = '0x483AE22AaEc52c0a1871C07E631d325bF5C8A08'
const PRICE = 0.001

// x402 payment required response
function x402PaymentRequired(res, endpoint) {
  return res.status(402).json({
    error: 'Payment Required',
    accepts: [{
      scheme: 'x402',
      currency: 'USDC',
      payTo: PAYTO,
      asset: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
      maxAmountRequired: PRICE
    }],
    x402Version: 1,
    maxAmountRequired: PRICE,
    price: PRICE,
    currency: 'USDC',
    payTo: PAYTO,
    description: `${endpoint} - requires USDC payment on Base`
  })
}

// Middleware to check payment (simplified - returns 402 if no payment)
function requirePayment(req, res, next) {
  const hasPayment = req.headers['x-payment'] || req.headers['payment-signature']
  // For demo, allow requests through - in production verify payment
  next()
}

// Status endpoint
app.get('/api/status', requirePayment, (req, res) => {
  res.json({
    success: true,
    platform: 'OpenClaw Status API',
    timestamp: new Date().toISOString(),
    endpoints: ['/api/status', '/api/geocode', '/api/weather'],
    agents: [
      { name: 'main', status: 'active' },
      { name: 'ceo', status: 'active' },
      { name: 'biz', status: 'active' },
      { name: 'polymarket', status: 'active' },
    ],
    cronJobs: [
      { name: 'Simmer Trading', schedule: '15min', status: 'active' },
      { name: 'CLAWMART Revenue', schedule: '12hr', status: 'active' },
      { name: 'VIRTUALS Scanner', schedule: '1day', status: 'active' },
    ]
  })
})

// Geocode endpoint - uses Nominatim (OpenStreetMap)
app.get('/api/geocode', requirePayment, async (req, res) => {
  const { q } = req.query
  if (!q) return res.status(400).json({ error: 'Missing q parameter (search query)' })
  
  try {
    const response = await axios.get(`https://nominatim.openstreetmap.org/search`, {
      params: { q, format: 'json', limit: 1 },
      headers: { 'User-Agent': 'OpenClaw/1.0' }
    })
    
    if (response.data.length === 0) {
      return res.status(404).json({ error: 'Location not found' })
    }
    
    const result = response.data[0]
    res.json({
      success: true,
      query: q,
      name: result.display_name,
      lat: parseFloat(result.lat),
      lon: parseFloat(result.lon),
      type: result.type,
    })
  } catch (error) {
    res.status(500).json({ error: 'Geocoding failed', details: error.message })
  }
})

// Weather endpoint - uses Open-Meteo (free, no key)
app.get('/api/weather', requirePayment, async (req, res) => {
  const { lat, lon } = req.query
  if (!lat || !lon) return res.status(400).json({ error: 'Missing lat/lon parameters' })
  
  const latNum = parseFloat(lat)
  const lonNum = parseFloat(lon)
  
  if (isNaN(latNum) || isNaN(lonNum)) {
    return res.status(400).json({ error: 'Invalid lat/lon values' })
  }
  
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${latNum}&longitude=${lonNum}&current=temperature_2m,weather_code,wind_speed_10m`
    const response = await axios.get(url)
    
    const data = response.data
    res.json({
      success: true,
      location: { lat: latNum, lon: lonNum },
      current: {
        temperature: data.current?.temperature_2m,
        weather_code: data.current?.weather_code,
        wind_speed: data.current?.wind_speed_10m,
      },
      timezone: data.timezone,
      source: 'Open-Meteo',
    })
  } catch (error) {
    res.status(500).json({ error: 'Weather fetch failed', details: error.message })
  }
})

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' })
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => console.log(`OpenClaw APIs running on port ${PORT}`))
