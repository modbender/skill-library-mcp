import { Stagehand, Page } from '@browserbasehq/stagehand';

export type Sport = 'tennis' | 'pickleball';

export interface TimeSlot {
  time: string;
  available: boolean;
}

export class BayClubBot {
  private stagehand: Stagehand | null = null;
  private page: Page | null = null;
  private isLoggedIn = false;
  private username: string;
  private password: string;

  constructor(username: string, password: string) {
    this.username = username;
    this.password = password;
  }

  /**
   * Initialize the browser
   */
  async init() {
    const isProduction = process.env.NODE_ENV === 'production';
    
    this.stagehand = new Stagehand({
      env: 'LOCAL',
      verbose: 1,
      localBrowserLaunchOptions: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
      },
      // Browserbase credentials (required for production)
      ...(isProduction && {
        apiKey: process.env.BROWSERBASE_API_KEY,
        projectId: process.env.BROWSERBASE_PROJECT_ID,
      }),
    });

    await this.stagehand.init();
    this.page = this.stagehand.context.pages()[0];
  }

  /**
   * Login to Bay Club Connect
   */
  async login() {
    if (!this.page) {
      throw new Error('Stagehand not initialized. Call init() first.');
    }

    try {
      console.log('Navigating to Bay Club Connect...');
      await this.page.goto('https://bayclubconnect.com/home/dashboard', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });

      console.log('Page loaded, checking current URL...');
      await this.page.waitForTimeout(3000);

      // Check if we're already logged in
      const isDashboard = this.page.url().includes('/home/dashboard');
      if (isDashboard) {
        try {
          await this.page.waitForSelector('text=Select Activity', { timeout: 3000 });
          console.log('Already logged in!');
          this.isLoggedIn = true;
          return;
        } catch (e) {
          console.log('Not logged in yet, proceeding with login...');
        }
      }

      console.log('Looking for login form...');
      const usernameField = this.page.locator('input[type="email"], input[type="text"]');
      
      await this.page.waitForSelector('input[type="email"], input[type="text"]', { timeout: 10000 });
      await usernameField.fill(this.username);

      const passwordField = this.page.locator('input[type="password"]');
      await passwordField.fill(this.password);

      // Click the submit button using evaluate to find it dynamically
      await this.page.evaluate(() => {
        const button = document.querySelector('button[type="submit"]') || 
                       Array.from(document.querySelectorAll('button')).find(b => 
                         b.textContent.toLowerCase().includes('log in') || 
                         b.textContent.toLowerCase().includes('sign in')
                       );
        if (button) button.click();
      });

      console.log('Waiting for navigation after login...');
      await this.page.waitForTimeout(5000);

      this.isLoggedIn = true;
      console.log('Successfully logged in!');
    } catch (error) {
      console.error('Login error:', error);
      throw new Error(`Failed to login: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Navigate to the booking page for a specific sport and day
   */
  async navigateToBooking(sport: Sport, day?: string) {
    if (!this.page || !this.isLoggedIn) {
      throw new Error('Must be logged in first. Call login().');
    }

    try {
      console.log(`Navigating to ${sport} booking...`);
      await this.page.goto('https://bayclubconnect.com/home/dashboard', {
        waitUntil: 'networkidle',
        timeout: 30000
      });
      await this.page.waitForTimeout(3000);

      // Club Selection (Gateway)
      const clubSelector = 'xpath=/html/body/app-root/div/app-dashboard/div/div/div[1]/div[1]/app-club-context-select/div/span[4]';
      await this.page.locator(clubSelector).click();
      
      const gatewayClub = 'xpath=/html/body/modal-container/div[2]/div/app-club-context-select-modal/div[2]/div/app-schedule-visit-club/div/div[1]/div/div[2]/div/div[3]/div[1]/div/div[2]/app-radio-select/div/div[2]/div/div[2]/div/span';
      await this.page.waitForSelector(gatewayClub);
      await this.page.locator(gatewayClub).click();

      const saveButton = 'xpath=/html/body/modal-container/div[2]/div/app-club-context-select-modal/div[2]/div/app-schedule-visit-club/div/div[2]/div/div';
      await this.page.locator(saveButton).click();
      await this.page.waitForTimeout(2000);

      // Navigate to Court Booking
      const scheduleActivity = 'xpath=/html/body/app-root/div/app-navbar/nav/div/div/button/span';
      await this.page.locator(scheduleActivity).click();
      
      const courtBooking = 'xpath=/html/body/app-root/div/app-schedule-visit/div/div/div[2]/div[1]/div[2]/div/div/img';
      await this.page.waitForSelector(courtBooking);
      await this.page.locator(courtBooking).click();
      await this.page.waitForTimeout(5000);

      // Sport Selection - use xpath for reliability
      console.log(`Selecting ${sport}...`);
      await this.page.waitForTimeout(2000);
      
      const sportXpaths = {
        tennis: 'xpath=/html/body/app-root/div/ng-component/app-racquet-sports-filter/div[1]/div[1]/div/div/app-court-booking-category-select/div/div[1]/div/div[2]',
        pickleball: 'xpath=/html/body/app-root/div/ng-component/app-racquet-sports-filter/div[1]/div[1]/div/div/app-court-booking-category-select/div/div[2]/div/div[2]'
      };
      
      try {
        await this.page.locator(sportXpaths[sport]).click({ timeout: 5000 });
        console.log(`✓ Selected ${sport} via xpath`);
      } catch (e) {
        console.warn(`Xpath failed for ${sport}, trying text-based...`);
        // Fallback to text-based
        const clicked = await this.page.evaluate((sportName: string) => {
          const allDivs = Array.from(document.querySelectorAll('div'));
          const sportEl = allDivs.find(el => {
            const text = el.textContent?.trim() || '';
            const hasNoChildren = el.children.length === 0;
            return hasNoChildren && text.toLowerCase() === sportName.toLowerCase();
          });
          
          if (sportEl) {
            const parent = sportEl.parentElement;
            if (parent) parent.click();
            (sportEl as HTMLElement).click();
            return true;
          }
          return false;
        }, sport);
        
        if (!clicked) {
          throw new Error(`Failed to select ${sport}`);
        }
      }
      
      await this.page.waitForTimeout(3000);

      // Duration Selection - different for each sport
      if (sport === 'tennis') {
        console.log('Selecting tennis duration (1.5 hours)...');
        await this.page.waitForTimeout(2000);
        
        const tennisXpath = 'xpath=/html/body/app-root/div/ng-component/app-racquet-sports-filter/div[1]/div[2]/div[2]/app-button-select/div/div[3]/span';
        try {
          await this.page.locator(tennisXpath).click({ timeout: 5000 });
          console.log('✓ Selected 1.5 hour duration');
        } catch (e) {
          console.warn('Could not select tennis duration via xpath');
        }
      } else {
        // Pickleball - try to find and click 60 minute option
        console.log('Selecting pickleball duration (60 minutes)...');
        await this.page.waitForTimeout(2000);
        
        const pickleballXpath = 'xpath=/html/body/app-root/div/ng-component/app-racquet-sports-filter/div[1]/div[2]/div[2]/app-button-select/div/div[2]/span';
        try {
          await this.page.locator(pickleballXpath).click({ timeout: 5000 });
          console.log('✓ Selected 60 minute duration');
        } catch (e) {
          console.warn('Pickleball duration xpath failed, checking if duration selector exists...');
          const exists = await this.page.evaluate(() => !!document.querySelector('app-button-select'));
          console.log('Duration selector exists:', exists);
        }
      }
      
      await this.page.waitForTimeout(1000);

      // Click Next button to proceed
      console.log('Clicking Next to continue...');
      const nextButton = 'xpath=/html/body/app-root/div/ng-component/app-racquet-sports-filter/div[2]/app-racquet-sports-reservation-summary/div/div/div/div/button';
      await this.page.locator(nextButton).click();
      await this.page.waitForTimeout(3000);

      // Day Selection
      const dayMap: { [key: string]: string } = {
        'monday': 'Mo', 'tuesday': 'Tu', 'wednesday': 'We', 'thursday': 'Th',
        'friday': 'Fr', 'saturday': 'Sa', 'sunday': 'Su'
      };
      const dayAbbrev = day ? dayMap[day.toLowerCase()] || 'Mo' : 'Mo';
      
      // Find and click the day element using text matching - click first match
      const dayXpath = `xpath=//*[text()="${dayAbbrev}"]`;
      const dayLocator = this.page.locator(dayXpath);
      await dayLocator.nth(0).click();

      await this.page.waitForTimeout(2000);

      // Switch to Hour View
      const hourViewSelector = 'xpath=//span[contains(text(), "HOUR VIEW")]';
      try {
        await this.page.waitForSelector(hourViewSelector, { timeout: 5000 });
        
        // Try multiple methods to click
        try {
          await this.page.locator(hourViewSelector).click();
          console.log('Clicked Hour View button via selector');
        } catch (e1) {
          // Try with evaluate
          await this.page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('span, button, div'));
            const hourViewBtn = buttons.find(b => b.textContent?.includes('HOUR VIEW'));
            if (hourViewBtn) {
              (hourViewBtn as HTMLElement).click();
              return true;
            }
            throw new Error('Hour View button not found');
          });
          console.log('Clicked Hour View button via evaluate');
        }
        
        await this.page.waitForTimeout(3000);
      } catch (e) {
        console.warn('Could not click Hour View, might already be active.');
      }
    } catch (error) {
      console.error('Navigation error:', error);
      throw error;
    }
  }

  /**
   * Get available time slots (filtered by booking duration)
   * Tennis: 1.5 hour (90 min) blocks
   * Pickleball: 1 hour (60 min) blocks
   * Returns slots as "START - END" format
   */
  async getAvailableTimes(sport: Sport = 'tennis'): Promise<string[]> {
    if (!this.page) throw new Error('Stagehand not initialized.');
    
    const durationMinutes = sport === 'tennis' ? 90 : 60;
    
    await this.page.waitForTimeout(5000);
    
    // Map grid positions to find which times have availability
    const times = await this.page.evaluate((duration: number) => {
      // 1. Get all time labels from the page
      const timeElements = Array.from(document.querySelectorAll('*')).filter(el => {
        const text = el.textContent?.trim() || '';
        return /^\d{1,2}:\d{2}\s*[AP]M$/.test(text) && el.children.length === 0;
      });
      
      // 2. Get their vertical positions
      const timePositions = timeElements.map(el => ({
        time: el.textContent?.trim() || '',
        top: el.getBoundingClientRect().top,
      }));
      
      // 3. Get all available (non-unavailable) time slots in the grid
      const allSlots = Array.from(document.querySelectorAll('.booking-calendar-column-time-slot'));
      const availableSlots = allSlots.filter(slot => 
        !slot.classList.contains('booking-calendar-column-time-slot-unavailable')
      );
      
      // 4. Get positions of available slots
      const availablePositions = availableSlots.map(slot => ({
        top: slot.getBoundingClientRect().top,
        height: slot.getBoundingClientRect().height,
      }));
      
      // 5. Match available slot positions to time labels
      const matchedTimes: string[] = [];
      
      for (const pos of availablePositions) {
        // Find closest time label
        let closestTime = '';
        let minDist = Infinity;
        
        for (const timePos of timePositions) {
          const dist = Math.abs(timePos.top - pos.top);
          if (dist < minDist) {
            minDist = dist;
            closestTime = timePos.time;
          }
        }
        
        // Only add if close enough and not already added
        if (closestTime && minDist < 50 && !matchedTimes.includes(closestTime)) {
          matchedTimes.push(closestTime);
        }
      }
      
      // Helper to parse time
      const parseTime = (t: string) => {
        const [time, period] = t.split(' ');
        const [hours, mins] = time.split(':').map(Number);
        let h = hours;
        if (period === 'PM' && h !== 12) h += 12;
        if (period === 'AM' && h === 12) h = 0;
        return h * 60 + mins;
      };
      
      // Helper to add minutes to a time string
      const addMinutes = (timeStr: string, minutesToAdd: number): string => {
        const mins = parseTime(timeStr);
        const newMins = mins + minutesToAdd;
        const hours = Math.floor(newMins / 60);
        const minutes = newMins % 60;
        
        let h = hours % 12;
        if (h === 0) h = 12;
        const period = hours >= 12 ? 'PM' : 'AM';
        
        return `${h}:${minutes.toString().padStart(2, '0')} ${period}`;
      };
      
      // Sort chronologically
      const sortedTimes = matchedTimes.sort((a, b) => parseTime(a) - parseTime(b));
      
      // Filter based on duration requirements passed in
      const slotsNeeded = duration / 30; // Number of 30-min slots needed
      
      const filteredSlots: string[] = [];
      
      for (let i = 0; i < sortedTimes.length; i++) {
        const startTime = sortedTimes[i];
        const startMins = parseTime(startTime);
        
        // Check if we have enough consecutive 30-minute slots
        let hasEnoughTime = true;
        for (let offset = 30; offset < duration; offset += 30) {
          const targetMins = startMins + offset;
          const hasSlot = sortedTimes.some(t => Math.abs(parseTime(t) - targetMins) < 5);
          if (!hasSlot) {
            hasEnoughTime = false;
            break;
          }
        }
        
        if (hasEnoughTime) {
          // Format as "START - END"
          const endTime = addMinutes(startTime, duration);
          filteredSlots.push(`${startTime} - ${endTime}`);
        }
      }
      
      return filteredSlots;
    }, durationMinutes);
    
    return times as string[];
  }

  /**
   * Book a court at the specified time
   */
  async bookCourt(time: string): Promise<boolean> {
    if (!this.page) throw new Error('Stagehand not initialized.');

    try {
      console.log(`Looking for bookable slot starting at ${time}...`);
      
      // Ensure we're in Hour View where .clickable.time-slot elements appear
      console.log('Ensuring Hour View is active...');
      await this.page.evaluate(() => {
        const all = Array.from(document.querySelectorAll('*'));
        const hourView = all.find(el => el.textContent?.trim() === 'HOUR VIEW');
        if (hourView) {
          (hourView as HTMLElement).click();
        }
      });
      
      await this.page.waitForTimeout(3000);
      
      // Find and click the time slot that starts with our target time
      const slotClicked = await this.page.evaluate((targetTime: string) => {
        const timeSlots = Array.from(document.querySelectorAll('.clickable.time-slot'));
        
        // Extract just the time part (e.g., "6:00 PM" → "6:00")
        const targetTimePart = targetTime.split(' ')[0]; // "6:00"
        
        for (const slot of timeSlots) {
          const lowercaseEl = slot.querySelector('.text-lowercase');
          if (lowercaseEl) {
            const text = lowercaseEl.textContent?.trim() || '';
            // Format is like "6:00  - 7:30 PM" or "7:00  - 8:30 AM"
            // Check if it starts with our target time
            if (text.startsWith(targetTimePart)) {
              (slot as HTMLElement).scrollIntoView({ block: 'center' });
              (slot as HTMLElement).click();
              console.log('Clicked time slot:', text);
              return true;
            }
          }
        }
        
        console.error('Could not find time slot for', targetTime);
        console.error('Available slots:', timeSlots.length);
        return false;
      }, time);

      if (!slotClicked) {
        console.error('Failed to click time slot');
        return false;
      }

      await this.page.waitForTimeout(2000);

      // Click Next/Continue button
      console.log('Looking for Next button...');
      try {
        const nextButton = this.page.locator('button:has-text("Next"), button:has-text("Continue")');
        await nextButton.click({ timeout: 5000 });
        console.log('Clicked Next button');
      } catch (e) {
        console.warn('Could not find Next button, trying xpath...');
        const nextXpath = 'xpath=/html/body/app-root/div/ng-component/app-racquet-sports-time-slot-select/div[2]/app-racquet-sports-reservation-summary/div/div/div/div[2]/button';
        await this.page.locator(nextXpath).click();
      }

      await this.page.waitForTimeout(3000);

      // Select buddy/partner - look for Samuel Wang or Emma Campbell
      console.log('Looking for buddy selection...');
      try {
        await this.page.waitForTimeout(3000);
        
        // Try to find and click Samuel Wang or Emma Campbell by name
        const buddySelected = await this.page.evaluate(() => {
          // Find all elements that might contain buddy/person info
          const allElements = Array.from(document.querySelectorAll('*'));
          
          // Look for Samuel Wang or Emma Campbell
          const samuelOrEmma = allElements.filter(el => {
            const text = el.textContent || '';
            return text.includes('Samuel Wang') || text.includes('Emma Campbell');
          });
          
          // Click the most specific (smallest) element
          if (samuelOrEmma.length > 0) {
            // Sort by text length to get most specific
            samuelOrEmma.sort((a, b) => 
              (a.textContent?.length || 999) - (b.textContent?.length || 999)
            );
            
            const buddy = samuelOrEmma[0] as HTMLElement;
            buddy.scrollIntoView({ block: 'center' });
            buddy.click();
            console.log('Selected buddy:', buddy.textContent?.trim().substring(0, 50));
            return true;
          }
          
          // Fallback: click any app-racquet-sports-person element
          const personElements = Array.from(document.querySelectorAll('app-racquet-sports-person'));
          if (personElements.length > 0) {
            (personElements[0] as HTMLElement).click();
            console.log('Selected first person element');
            return true;
          }
          
          console.log('No buddy elements found');
          return false;
        });
        
        if (buddySelected) {
          console.log('✓ Buddy selected');
          await this.page.waitForTimeout(2000);
        } else {
          console.log('⚠ No buddy selection made');
        }
      } catch (e) {
        console.log('Buddy selection error:', e);
      }
      
      // Step before confirming: Check for any required checkboxes (terms, policies, etc.)
      console.log('Checking for required checkboxes...');
      await this.page.evaluate(() => {
        const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
        checkboxes.forEach(cb => {
          if (!(cb as HTMLInputElement).checked) {
            (cb as HTMLInputElement).click();
            console.log('Checked a checkbox');
          }
        });
      });
      
      await this.page.waitForTimeout(1000);
      
      // Click Final Confirm Booking button
      console.log('Looking for Confirm Booking button...');
      try {
        // Look for "CONFIRM BOOKING" button specifically
        const confirmButton = this.page.locator('button:has-text("CONFIRM BOOKING")').first();
        
        // Wait a bit for it to become enabled after buddy selection
        await this.page.waitForTimeout(2000);
        
        await confirmButton.click({ timeout: 5000 });
        console.log('Clicked Confirm Booking - booking should be complete!');
      } catch (e) {
        console.error('Confirm button error:', e);
        // Try clicking any enabled Confirm button
        const clicked = await this.page.evaluate(() => {
          const buttons = Array.from(document.querySelectorAll('button'));
          const confirmBtn = buttons.find(b => 
            b.textContent?.includes('CONFIRM') && 
            b.textContent?.includes('BOOKING') &&
            !(b as HTMLButtonElement).disabled
          );
          if (confirmBtn) {
            (confirmBtn as HTMLElement).click();
            console.log('Clicked enabled confirm button via evaluate');
            return true;
          } else {
            console.error('All confirm buttons are still disabled');
            return false;
          }
        });
        
        if (!clicked) {
          throw new Error('Could not click Confirm button - it may still be disabled');
        }
      }
      
      await this.page.waitForTimeout(3000);
      
      return true;
    } catch (error) {
      console.error('Booking error:', error);
      return false;
    }
  }

  async close() {
    if (this.stagehand) {
      await this.stagehand.close();
      this.isLoggedIn = false;
    }
  }
}
