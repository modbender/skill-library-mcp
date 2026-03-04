import { apiPublicGet } from '../lib/api.js';

async function main() {
  const result = await apiPublicGet('/api/search/categories');

  console.log('Available categories:');
  for (const cat of result.categories) {
    console.log(`  - ${cat}`);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
