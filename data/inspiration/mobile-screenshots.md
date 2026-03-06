# Mobile App Screenshots — Deep Dive

Finding the right mobile UI references by platform, category, and pattern.

## Primary Sources

### Mobbin (https://mobbin.com)

**The gold standard for mobile UI research.**

**Features:**
- iOS and Android coverage
- Filter by screen type (onboarding, settings, profile, etc.)
- Filter by app category (finance, health, social, etc.)
- User flow recordings
- Updated regularly with new apps

**Best practices:**
- Use specific filters, not general browsing
- Save screens to collections for projects
- Note the app name for context

**Pricing:** Free tier limited, paid for full access

### Screenlane (https://screenlane.com)

**Complementary to Mobbin with different curation.**

**Features:**
- Mobile screens by category
- Clean interface
- Good for quick browsing

**Best for:** Quick pattern lookup, specific component ideas

### Page Flows (https://pageflows.com)

**Focus: Complete user flows, not just static screens.**

**Features:**
- Video recordings of real flows
- Onboarding, checkout, settings flows
- See transitions and micro-interactions

**Best for:** Understanding how screens connect, UX flow design

**Pricing:** Paid subscription

### UI Sources (https://uisources.com)

**Deep dives into specific apps.**

**Features:**
- Full app breakdowns
- Design system analysis
- Every screen documented

**Best for:** Studying how one app handles everything

**Pricing:** Paid subscription

## By Screen Type

### Onboarding

| Pattern | Where to Find | Examples |
|---------|---------------|----------|
| Carousel intro | Mobbin → Onboarding | Headspace, Calm |
| Value prop screens | Page Flows → Onboarding | Notion, Linear |
| Sign up flow | Screenlane → Authentication | Most apps |
| Permissions ask | Page Flows | Health apps |
| Tutorial overlays | Mobbin → Tutorials | Figma mobile |

### Authentication

| Pattern | Where to Find | Examples |
|---------|---------------|----------|
| Social login | Mobbin → Login | Spotify, Airbnb |
| Phone + OTP | Page Flows | WhatsApp, Uber |
| Email magic link | Screenlane | Slack, Notion |
| Biometric prompt | Mobbin → Login | Banking apps |
| Password reset | Page Flows | Any major app |

### Home / Dashboard

| Pattern | Where to Find | Examples |
|---------|---------------|----------|
| Card-based feed | Mobbin → Home | Instagram, Twitter |
| Stats dashboard | Mobbin → Dashboard | Fitness apps |
| Quick actions | Screenlane → Home | Banking apps |
| Search-first | Mobbin | Spotify, YouTube |
| Tab-based nav | Most apps | Standard pattern |

### Profile / Settings

| Pattern | Where to Find | Examples |
|---------|---------------|----------|
| Edit profile | Mobbin → Profile | LinkedIn, Twitter |
| Settings list | Mobbin → Settings | iOS Settings |
| Account management | Page Flows | Subscription apps |
| Privacy settings | Page Flows | Social apps |
| Preferences | Screenlane | Most apps |

### E-commerce

| Pattern | Where to Find | Examples |
|---------|---------------|----------|
| Product grid | Mobbin → E-commerce | Amazon, ASOS |
| Product detail | Screenlane → Product | Any shop app |
| Cart | Page Flows → Checkout | Shopify stores |
| Checkout flow | Page Flows | Critical flow |
| Order tracking | Mobbin | Amazon, food delivery |

### Content / Media

| Pattern | Where to Find | Examples |
|---------|---------------|----------|
| Article reader | Mobbin → Reading | Medium, Substack |
| Video player | Screenlane | YouTube, TikTok |
| Image gallery | Mobbin → Gallery | Instagram, VSCO |
| Audio player | Mobbin → Music | Spotify, Podcasts |
| Carousel stories | Instagram, Snapchat | Stories format |

## By App Category

### Fintech / Banking

**Reference apps:**
- Revolut (modern, feature-rich)
- Nubank (clean, focused)
- Cash App (simple, bold)
- Robinhood (data-heavy done well)

**Key patterns to study:**
- Transaction lists
- Balance display
- Send/receive flows
- Card management
- Security UX

### Health & Fitness

**Reference apps:**
- Apple Fitness (native excellence)
- Strava (social fitness)
- Headspace (calm, focused)
- Oura (data visualization)
- MyFitnessPal (logging UX)

**Key patterns:**
- Activity rings/progress
- Workout tracking
- Health metrics display
- Streak/gamification
- Meditation/timer UI

### Social / Communication

**Reference apps:**
- Instagram (stories, feed, DMs)
- Discord (communities, chat)
- Slack (work messaging)
- BeReal (unique capture flow)
- Threads (Twitter alternative)

**Key patterns:**
- Feed algorithms feel
- Messaging UI
- Notifications
- Profile customization
- Content creation

### Productivity

**Reference apps:**
- Notion (complex made simple)
- Linear (speed, keyboard shortcuts)
- Things 3 (iOS design excellence)
- Todoist (cross-platform)
- Obsidian (power users)

**Key patterns:**
- List/board views
- Quick capture
- Search and filter
- Keyboard shortcuts
- Sync indicators

### Travel / Booking

**Reference apps:**
- Airbnb (gold standard)
- Booking.com (lots of info, clean)
- Uber (maps, ETA, payment)
- Google Maps (complex data, simple UI)

**Key patterns:**
- Search with dates/filters
- Map integration
- Booking flow
- Pricing display
- Reviews/ratings

## Platform-Specific Patterns

### iOS

**Human Interface Guidelines patterns:**
- Navigation bars with large titles
- Tab bars (max 5 items)
- Sheets and modals
- Swipe gestures
- Haptic feedback moments

**Where to study:**
- Apple's own apps (Notes, Reminders, Health)
- Apps featured in App Store Today
- WWDC design session videos

### Android (Material You)

**Material Design 3 patterns:**
- Dynamic color from wallpaper
- Large touch targets
- Bottom navigation
- FAB placement
- Gesture navigation

**Where to study:**
- Google apps (Keep, Messages, Photos)
- Material Design gallery
- Android apps on Mobbin

### Cross-Platform Considerations

**What to watch:**
- Native vs custom components
- Platform-specific navigation
- Gesture expectations
- Typography (SF Pro vs Roboto)
- Icon styles

## Workflow Tips

### Building a Reference Library

1. **Create project in Mobbin** (if paid) or use Figma
2. **Organize by screen type**, not by app
3. **Screenshot everything** — URLs change
4. **Note what you like** about each reference
5. **Tag with keywords** for future search

### Effective Browsing

**Don't:** Browse randomly hoping for inspiration
**Do:** Search for specific patterns you need

Example process:
1. "I need a settings screen for a fintech app"
2. Mobbin → Filter: Finance → Screen: Settings
3. Review 10-15 examples
4. Save 3-5 best to collection
5. Identify common patterns and unique ideas

### Translating References

**From screenshot to your app:**
1. Don't copy exactly — extract the principle
2. Consider your brand voice
3. Test with your actual content
4. Iterate based on user feedback

### Staying Current

**Apps change constantly.** Sources to watch:
- Mobbin's "Recently Added"
- App Store "Today" features
- Designer Twitter/Threads
- ProductHunt new launches
