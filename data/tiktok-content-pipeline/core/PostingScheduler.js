/**
 * PostingScheduler - Smart posting frequency and timing engine
 * 
 * Handles posting frequency based on account age:
 * - New accounts (0-30 days): Daily posting at optimal times
 * - Transition (25-30 days): Gradual taper to 4 posts/week
 * - Established (31+ days): 3-4 posts/week on optimal days
 * 
 * Uses research-backed optimal timing for maximum engagement.
 */

class PostingScheduler {
  constructor(config) {
    this.config = config;
    this.timezone = config.posting?.timezone || 'Europe/London';
    
    // Research-backed optimal posting times
    this.optimalTimes = {
      // Best days: Tuesday, Wednesday, Thursday
      0: [12, 18], // Sunday - fallback times
      1: [12, 18], // Monday - fallback times  
      2: [17],     // Tuesday - 5pm optimal
      3: [14, 15, 16, 17], // Wednesday - 2-5pm optimal
      4: [15, 16, 17], // Thursday - 3-5pm optimal
      5: [12, 18], // Friday - fallback times
      6: [12, 18]  // Saturday - fallback times
    };
    
    // Best engagement days (prioritized)
    this.optimalDays = [2, 3, 4]; // Tuesday, Wednesday, Thursday
    this.fallbackDays = [1, 5, 0, 6]; // Monday, Friday, Sunday, Saturday
  }

  /**
   * Get account age in days since creation
   */
  getAccountAge() {
    if (!this.config.account?.createdAt) {
      throw new Error('Account createdAt timestamp not found in config');
    }
    
    const createdAt = new Date(this.config.account.createdAt);
    const now = new Date();
    const diffMs = now.getTime() - createdAt.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    return Math.max(0, diffDays);
  }

  /**
   * Check if account is in new account phase (< 30 days)
   */
  isNewAccount() {
    return this.getAccountAge() < 30;
  }

  /**
   * Get target posts per week based on account age
   */
  getPostsPerWeek() {
    const age = this.getAccountAge();
    
    if (age < 25) {
      return 7; // Daily posting
    } else if (age < 31) {
      // Transition period: taper from 7 to 4
      // Day 25: 6 posts, Day 26: 5 posts, Day 27-30: 4 posts
      if (age === 25) return 6;
      if (age === 26) return 5;
      return 4;
    } else {
      return this._getEstablishedFrequency(); // 3-4 posts/week
    }
  }

  /**
   * Get next optimal posting slot considering recent posts
   * @param {Array} recentPosts - Array of {publishDate: ISO string}
   * @returns {Date} - Next optimal posting time
   */
  getNextPostingSlot(recentPosts = []) {
    const now = new Date();
    const recentDates = recentPosts.map(p => new Date(p.publishDate));
    
    // Check if already posted today
    const today = this._getDateInTimezone(now);
    const hasPostedToday = recentDates.some(date => 
      this._isSameDay(date, today)
    );
    
    if (hasPostedToday) {
      // Find next available day
      return this._getNextAvailableSlot(recentDates, 1);
    }
    
    // Check if should post today based on schedule
    if (this.shouldPostToday(recentPosts)) {
      return this._getOptimalTimeToday();
    }
    
    // Find next scheduled day
    return this._getNextAvailableSlot(recentDates, 0);
  }

  /**
   * Get posting schedule for a week starting from given date
   * @param {Date} weekStartDate - Start of week (should be Monday)
   * @returns {Array<Date>} - Array of posting times for the week
   */
  getWeekSchedule(weekStartDate) {
    const postsPerWeek = this.getPostsPerWeek();
    const schedule = [];
    
    if (postsPerWeek === 7) {
      // New account: daily posting
      for (let i = 0; i < 7; i++) {
        const date = new Date(weekStartDate);
        date.setDate(date.getDate() + i);
        const dayOfWeek = date.getDay();
        const hour = this._getBestHourForDay(dayOfWeek);
        
        date.setHours(hour, 0, 0, 0);
        schedule.push(date);
      }
    } else {
      // Established account: prioritize optimal days
      const targetDays = this._getTargetDaysForWeek(postsPerWeek);
      
      targetDays.forEach(dayOffset => {
        const date = new Date(weekStartDate);
        date.setDate(date.getDate() + dayOffset);
        const dayOfWeek = date.getDay();
        const hour = this._getBestHourForDay(dayOfWeek);
        
        date.setHours(hour, 0, 0, 0);
        schedule.push(date);
      });
    }
    
    return schedule.sort((a, b) => a.getTime() - b.getTime());
  }

  /**
   * Quick check: should we post today based on frequency and recent posts?
   * @param {Array} recentPosts - Array of {publishDate: ISO string}
   * @returns {boolean}
   */
  shouldPostToday(recentPosts = []) {
    const now = new Date();
    const today = this._getDateInTimezone(now);
    const recentDates = recentPosts.map(p => new Date(p.publishDate));
    
    // Never post if already posted today
    const hasPostedToday = recentDates.some(date => 
      this._isSameDay(date, today)
    );
    if (hasPostedToday) return false;
    
    // For new accounts: post daily
    if (this.isNewAccount()) return true;
    
    // For established accounts: check if today is scheduled
    const postsPerWeek = this.getPostsPerWeek();
    const targetDays = this._getTargetDaysForWeek(postsPerWeek);
    const todayOffset = this._getDayOfWeekOffset(today);
    
    return targetDays.includes(todayOffset);
  }

  // Private helper methods

  _getEstablishedFrequency() {
    // Vary between 3-4 posts/week for established accounts
    // Could be based on performance metrics in the future
    return 4;
  }

  _getBestHourForDay(dayOfWeek) {
    const hours = this.optimalTimes[dayOfWeek];
    // Return first (primary) optimal hour for the day
    return hours[0];
  }

  _getTargetDaysForWeek(postsPerWeek) {
    const optimalDays = [1, 2, 3]; // Monday=0, so Tue=1, Wed=2, Thu=3
    const fallbackDays = [0, 4, 5, 6]; // Mon, Fri, Sat, Sun
    
    if (postsPerWeek <= 3) {
      return optimalDays.slice(0, postsPerWeek);
    } else if (postsPerWeek === 4) {
      return [...optimalDays, fallbackDays[0]]; // Add Monday
    } else if (postsPerWeek === 5) {
      return [...optimalDays, fallbackDays[0], fallbackDays[1]]; // Add Mon, Fri
    } else if (postsPerWeek === 6) {
      return [...optimalDays, ...fallbackDays.slice(0, 3)]; // Add Mon, Fri, Sat
    } else {
      return [0, 1, 2, 3, 4, 5, 6]; // All days
    }
  }

  _getOptimalTimeToday() {
    const now = new Date();
    const today = this._getDateInTimezone(now);
    const dayOfWeek = today.getDay();
    const hour = this._getBestHourForDay(dayOfWeek);
    
    // Set to optimal time for today
    const optimalTime = new Date(today);
    optimalTime.setHours(hour, 0, 0, 0);
    
    // If optimal time has passed, schedule for tomorrow
    if (optimalTime <= now) {
      return this._getNextAvailableSlot([], 1);
    }
    
    return optimalTime;
  }

  _getNextAvailableSlot(recentDates, daysFromNow = 0) {
    const now = new Date();
    let candidate = new Date(now);
    candidate.setDate(candidate.getDate() + daysFromNow);
    
    const postsPerWeek = this.getPostsPerWeek();
    
    // For established accounts, find next optimal day
    if (!this.isNewAccount()) {
      const targetDays = this._getTargetDaysForWeek(postsPerWeek);
      
      for (let i = 0; i < 14; i++) { // Search up to 2 weeks
        const testDate = new Date(candidate);
        testDate.setDate(testDate.getDate() + i);
        const dayOffset = this._getDayOfWeekOffset(testDate);
        
        const hasPostedThisDay = recentDates.some(date => 
          this._isSameDay(date, testDate)
        );
        
        if (targetDays.includes(dayOffset) && !hasPostedThisDay) {
          const dayOfWeek = testDate.getDay();
          const hour = this._getBestHourForDay(dayOfWeek);
          testDate.setHours(hour, 0, 0, 0);
          return testDate;
        }
      }
    }
    
    // For new accounts or fallback: next day at optimal time
    candidate.setDate(candidate.getDate() + 1);
    const dayOfWeek = candidate.getDay();
    const hour = this._getBestHourForDay(dayOfWeek);
    candidate.setHours(hour, 0, 0, 0);
    
    return candidate;
  }

  _getDateInTimezone(date) {
    // Simple timezone handling using built-in Date methods
    // This is a basic implementation - for production might need more robust solution
    return new Date(date.toLocaleString('en-US', { timeZone: this.timezone }));
  }

  _isSameDay(date1, date2) {
    const d1 = this._getDateInTimezone(date1);
    const d2 = this._getDateInTimezone(date2);
    
    return d1.getFullYear() === d2.getFullYear() &&
           d1.getMonth() === d2.getMonth() &&
           d1.getDate() === d2.getDate();
  }

  _getDayOfWeekOffset(date) {
    // Return day offset from Monday (Monday = 0, Tuesday = 1, etc.)
    const dayOfWeek = date.getDay();
    return dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Convert Sunday=0 to Sunday=6
  }

  /**
   * Get human-readable account phase
   */
  getAccountPhase() {
    const age = this.getAccountAge();
    
    if (age < 25) return 'New Account (Daily Posting)';
    if (age < 31) return 'Transition Phase (Tapering Down)';
    return 'Established Account (Optimal Schedule)';
  }

  /**
   * Check if any posts are overdue based on schedule
   * @param {Array} recentPosts - Recent posts with publishDate
   * @returns {boolean}
   */
  isOverdue(recentPosts = []) {
    const now = new Date();
    const lastWeek = new Date(now);
    lastWeek.setDate(lastWeek.getDate() - 7);
    
    const schedule = this.getWeekSchedule(lastWeek);
    const recentDates = recentPosts.map(p => new Date(p.publishDate));
    
    return schedule.some(scheduledTime => {
      if (scheduledTime > now) return false; // Future posts can't be overdue
      
      // Check if we posted within 24 hours of scheduled time
      const posted = recentDates.some(postDate => {
        const diffHours = Math.abs(postDate.getTime() - scheduledTime.getTime()) / (1000 * 60 * 60);
        return diffHours < 24;
      });
      
      return !posted;
    });
  }
}

module.exports = PostingScheduler;