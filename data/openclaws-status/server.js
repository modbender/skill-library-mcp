const express = require('express')
const axios = require('axios')

const app = express()
app.use(express.json())

const PAYTO = '0x483AE22AaEc52c0a1871C07E631d325b3F5C8A08'

// x402 payment response helper
function paymentRequired(res, endpoint) {
  return res.status(402).json({
    error: 'Payment Required',
    accepts: [{
      scheme: 'x402',
      currency: 'USDC',
      payTo: PAYTO,
      asset: 'USDC',
      maxAmountRequired: 0.001
    }],
    maxAmountRequired: 0.001,
    price: 0.001,
    currency: 'USDC',
    payTo: PAYTO
  })
}

// Check for payment header (simplified)
function checkPayment(req, res, next) {
  const payment = req.headers['x-payment'] || req.headers['payment-signature']
  // For now, allow free access - add payment verification later
  next()
}

// Status endpoint
app.get('/api/status', checkPayment, (req, res) => {
  res.json({
    success: true,
    platform: 'OpenClaw',
    timestamp: new Date().toISOString(),
    agents: [
      { name: 'main', status: 'active' },
      { name: 'ceo', status: 'active' },
      { name: 'biz', status: 'active' },
    ],
  })
})

// Geocode endpoint - free (Nominatim)
app.get('/api/geocode', checkPayment, async (req, res) => {
  const { q } = req.query
  if (!q) return res.status(400).json({ error: 'Missing q parameter' })
  
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
      name: result.display_name,
      lat: parseFloat(result.lat),
      lon: parseFloat(result.lon),
    })
  } catch (error) {
    res.status(500).json({ error: 'Geocoding failed' })
  }
})

// Weather endpoint - free (Open-Meteo)
app.get('/api/weather', checkPayment, async (req, res) => {
  const { lat, lon } = req.query
  if (!lat || !lon) return res.status(400).json({ error: 'Missing lat/lon' })
  
  try {
    const response = await axios.get(`https://api.open-meteo.com/v1/forecast`, {
      params: {
        latitude: lat,
        longitude: lon,
        current: 'temperature_2m,weather_code,wind_speed_10m',
        timezone: 'auto'
      }
    })
    
    const data = response.data
    res.json({
      success: true,
      location: { lat, lon },
      temperature: data.current?.temperature_2m,
      weather: data.current?.weather_code,
      wind: data.current?.wind_speed_10m,
      timezone: data.timezone,
    })
  } catch (error) {
    res.status(500).json({ error: 'Weather fetch failed' })
  }
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => console.log(`OpenClaw APIs running on port ${PORT}`))
