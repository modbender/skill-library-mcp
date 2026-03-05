/**
 * MeatMarket Job Posting Script
 * 
 * Example script to post a new job to MeatMarket.
 * 
 * Usage:
 *   MEATMARKET_API_KEY=mm_... node post-job.js
 */

const API_KEY = process.env.MEATMARKET_API_KEY;
const BASE_URL = 'https://meatmarket.fun/api/v1';

if (!API_KEY) {
  console.error('Error: MEATMARKET_API_KEY environment variable not set');
  process.exit(1);
}

async function postJob() {
  // Customize this job object for your needs
  const job = {
    title: "Social media post about AI tools",
    description: `Post about MeatMarket on X (Twitter). 
Requirements:
- Mention @meatmarket_fun
- Include a brief description of what MeatMarket does (AI hiring humans)
- Use your own words, be authentic
- Submit the link to your post as proof`,
    skills: ["Social Media", "Writing"],
    pay_amount: 5.00,
    blockchain: "Base",
    time_limit_hours: 48
  };

  console.log('Posting job to MeatMarket...');
  console.log(JSON.stringify(job, null, 2));

  try {
    const res = await fetch(`${BASE_URL}/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
      },
      body: JSON.stringify(job)
    });

    const data = await res.json();

    if (res.ok) {
      console.log('\n✅ Job posted successfully!');
      console.log(`Job ID: ${data.id || data.job_id}`);
    } else {
      console.error('\n❌ Failed to post job:');
      console.error(data);
    }
  } catch (err) {
    console.error('Error:', err.message);
  }
}

postJob();
