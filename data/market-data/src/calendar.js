import https from 'https';

const CALENDAR_URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.xml';

/**
 * Fetches the economic calendar for the current week from ForexFactory.
 * @param {Object} params
 * @param {string} [params.importance] - Filter by impact: 'High', 'Medium', 'Low', or 'All'. Default: 'High'.
 * @param {string} [params.currencies] - Comma-separated list of currencies to filter (e.g., 'USD,EUR'). Default: All.
 * @returns {Promise<string>} A formatted string of upcoming economic events.
 */
export async function fetch_economic_calendar({ importance = 'High', currencies }) {
  return new Promise((resolve, reject) => {
    https.get(CALENDAR_URL, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          // Simple XML parsing using Regex to avoid heavy dependencies
          // Structure: <event><title>...</title><country>...</country><date>...</date><time>...</time><impact>...</impact>...</event>
          
          const events = [];
          const eventRegex = /<event>([\s\S]*?)<\/event>/g;
          let match;

          while ((match = eventRegex.exec(data)) !== null) {
            const eventBlock = match[1];
            
            const getTag = (tag) => {
              const m = new RegExp(`<${tag}>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?<\/${tag}>`).exec(eventBlock);
              return m ? m[1] : '';
            };

            const title = getTag('title');
            const country = getTag('country');
            const date = getTag('date');
            const time = getTag('time');
            const impact = getTag('impact');
            const forecast = getTag('forecast');
            const previous = getTag('previous');

            events.push({ title, country, date, time, impact, forecast, previous });
          }

          // Filter
          const importanceMap = { 'High': 3, 'Medium': 2, 'Low': 1, 'Holiday': 0 };
          const minImpact = importanceMap[importance] || 3;

          const filtered = events.filter(e => {
            // Impact Check
            const eventImpact = importanceMap[e.impact] || 0;
            if (importance !== 'All' && eventImpact < minImpact) return false;

            // Currency Check
            if (currencies) {
              const allowed = currencies.toUpperCase().split(',').map(c => c.trim());
              if (!allowed.includes(e.country)) return false;
            }
            
            return true;
          });

          if (filtered.length === 0) {
            resolve(`No ${importance} impact events found for the specified currencies.`);
            return;
          }

          // Sort by date/time (XML is usually sorted but good to ensure)
          // Note: Date parsing is tricky without moment/date-fns, assuming XML order is chronological or "MM-DD-YYYY"
          
          let output = `📅 Economic Calendar (Importance: ${importance}+)\n`;
          output += `Date       | Time    | Cur | Impact | Event                          | Fcst   | Prev\n`;
          output += `-----------|---------|-----|--------|--------------------------------|--------|--------\n`;

          filtered.slice(0, 20).forEach(e => { // Limit to top 20 to avoid spam
            const title = e.title.length > 30 ? e.title.substring(0, 27) + '...' : e.title.padEnd(30);
            output += `${e.date} | ${e.time.padEnd(7)} | ${e.country} | ${e.impact.padEnd(6)} | ${title} | ${e.forecast.padEnd(6)} | ${e.previous}\n`;
          });
          
          if (filtered.length > 20) {
              output += `... and ${filtered.length - 20} more events.\n`;
          }

          resolve(output);

        } catch (error) {
          resolve(`Error parsing calendar data: ${error.message}`);
        }
      });

    }).on('error', (err) => {
      resolve(`Network error fetching calendar: ${err.message}`);
    });
  });
}
