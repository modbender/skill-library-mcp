const https = require('https');

// Parse args
const args = process.argv.slice(2);
let origin = '';
let destination = '';
let mode = 'DRIVE';
let apiKey = process.env.GOOGLE_ROUTES_API_KEY || '';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--origin') origin = args[i + 1];
  if (args[i] === '--destination') destination = args[i + 1];
  if (args[i] === '--mode') mode = args[i + 1];
}

if (!origin || !destination) {
  console.error('Error: --origin and --destination are required');
  process.exit(1);
}

if (!apiKey) {
    console.error('Error: API Key required. Set GOOGLE_ROUTES_API_KEY env var.');
    process.exit(1);
}

// Helper to geocode address to LatLng (using helper function or assuming text input supported by ComputeRoutes if using proper field)
// NOTE: ComputeRoutes v2 supports "address" string in "address" field inside origin/destination!
// We don't need manual geocoding.

const requestBody = JSON.stringify({
  origin: {
    address: origin
  },
  destination: {
    address: destination
  },
  travelMode: mode,
  routingPreference: mode === 'DRIVE' ? 'TRAFFIC_AWARE' : undefined,
  computeAlternativeRoutes: false,
  routeModifiers: {
    avoidTolls: false,
    avoidHighways: false,
    avoidFerries: false
  },
  languageCode: "es-419",
  units: "METRIC"
});

const options = {
  hostname: 'routes.googleapis.com',
  path: '/directions/v2:computeRoutes',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': apiKey,
    'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.staticDuration,routes.description'
  }
};

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode !== 200) {
      console.error(`API Error (${res.statusCode}):`, data);
      process.exit(1);
    }

    try {
      const response = JSON.parse(data);
      if (!response.routes || response.routes.length === 0) {
        console.log("No routes found.");
        return;
      }

      const route = response.routes[0];
      const durationSeconds = parseInt(route.duration.replace('s', ''));
      const distanceMeters = route.distanceMeters;

      const minutes = Math.floor(durationSeconds / 60);
      const km = (distanceMeters / 1000).toFixed(1);

      // Generate Google Maps Link
      const mapsLink = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&travelmode=driving`;

      console.log(JSON.stringify({
          origin,
          destination,
          mode,
          duration: `${minutes} min`,
          distance: `${km} km`,
          traffic_duration_seconds: durationSeconds,
          route_link: mapsLink
      }, null, 2));

    } catch (e) {
      console.error("Error parsing response:", e);
    }
  });
});

req.on('error', (e) => {
  console.error(`Request error: ${e.message}`);
});

req.write(requestBody);
req.end();
