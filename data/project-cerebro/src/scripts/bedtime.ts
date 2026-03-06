import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { format, toZonedTime } from 'date-fns-tz';

const execAsync = promisify(exec);
const TIMEZONE = 'America/Chicago';

async function getSchedule(): Promise<string> {
  const scriptPath = path.join(process.cwd(), 'dist', 'scripts', 'get-schedule.js');
  const { stdout } = await execAsync(`node ${scriptPath}`);
  return stdout;
}

function parseTimes(lines: string[]): Date[] {
  const dates: Date[] = [];
  for (const line of lines) {
    const match = line.match(/\*\*(\d{1,2}:\d{2} [AP]M) - (\d{1,2}:\d{2} [AP]M)\*\*/);
    if (match) {
      const timeStr = match[1];
      const today = new Date();
      const day = format(toZonedTime(today, TIMEZONE), 'yyyy-MM-dd', { timeZone: TIMEZONE });
      const dt = new Date(`${day} ${timeStr}`);
      dates.push(dt);
    }
  }
  return dates;
}

async function main() {
  const schedule = await getSchedule();
  const lines = schedule.split('\n');
  const today = new Date();
  const tomorrow = format(new Date(today.getTime() + 24*60*60*1000), 'EEEE, MMMM d', { timeZone: TIMEZONE });

  let inTomorrow = false;
  const tomorrowLines: string[] = [];
  for (const line of lines) {
    if (line.startsWith('## ')) {
      inTomorrow = line.includes(tomorrow);
      continue;
    }
    if (inTomorrow) tomorrowLines.push(line);
  }

  const times = parseTimes(tomorrowLines).sort((a,b)=>a.getTime()-b.getTime());
  if (times.length === 0) {
    console.log('No events found for tomorrow.');
    return;
  }

  const earliest = times[0];
  const bedtime = new Date(earliest.getTime() - 10*60*60*1000);
  const bedStr = format(toZonedTime(bedtime, TIMEZONE), 'h:mm a', { timeZone: TIMEZONE });
  const earlyStr = format(toZonedTime(earliest, TIMEZONE), 'h:mm a', { timeZone: TIMEZONE });

  console.log(`Earliest event: ${earlyStr} (tomorrow)`);
  console.log(`Latest bedtime: ${bedStr} (10 hours before)`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
