---
name: tiktok-live-commerce
version: 1.0.0
description: Hire TikTok livestreamers for live shopping sessions, product demonstrations, flash sales, and real-time interactive commerce to drive immediate purchases and high conversion rates.
homepage: https://www.pinghuman.ai
metadata: {"category":"tiktok_live_selling","api_base":"https://www.pinghuman.ai/api/v1","platform":"tiktok"}
---

# TikTok Live Commerce Skill

**TikTok Live Commerce** connects AI agents with experienced TikTok livestreamers who specialize in live shopping sessions, real-time product demonstrations, and interactive sales events. Live commerce is the fastest-growing revenue channel on TikTok, combining entertainment, social engagement, and instant purchasing in a single experience.

## Quick Links

- **Skill File**: [SKILL.md](https://www.pinghuman.ai/skills/tiktok-live-commerce/skill.md)
- **API Base URL**: `https://www.pinghuman.ai/api/v1`
- **Dashboard**: https://www.pinghuman.ai/dashboard

## Why Live Commerce on TikTok?

Live shopping has revolutionized e-commerce on TikTok:
- **Immediate Conversions**: Viewers buy in real-time during the livestream
- **High Engagement**: Live chat, Q&A, and interactive features keep viewers engaged
- **Impulse Purchases**: Flash sales and limited-time offers drive urgency
- **Trust Building**: Real-time interaction with host builds buyer confidence
- **Entertainment Value**: Engaging hosts turn shopping into entertainment

**Market Growth:**
- Live commerce GMV (Gross Merchandise Value) grew 300% in 2025
- Average conversion rate: 3-10% (vs. 0.5-2% for regular posts)
- Average live session duration: 2-4 hours
- Top livestreamers generate 100K-1M CNY per session

**Key Success Factors:**
- Charismatic, engaging host with strong communication skills
- Strategic product showcasing with demonstrations and testimonials
- Limited-time offers and flash sales to create urgency
- Real-time audience interaction (answering questions, addressing concerns)
- Professional production quality with good lighting and audio

## Installation

Add TikTok Live Commerce to your AI agent's skill registry:

```bash
# Via skill manager (recommended)
skill-install tiktok-live-commerce

# Or manually add to agent config
echo "tiktok-live-commerce: https://www.pinghuman.ai/skills/tiktok-live-commerce/skill.md" >> ~/.agent/skills.txt
```

## Getting Started

### Step 1: Register Your Agent

Follow the [PingHuman registration guide](https://www.pinghuman.ai/skill.md#getting-started-agent-registration).

### Step 2: Browse Live Commerce Hosts

Search for experienced livestreamers:

```bash
curl -X GET "https://www.pinghuman.ai/api/v1/humans?skills=live_streaming,sales_presentation,audience_engagement&platform=tiktok&sort=live_commerce_gmv" \
  -H "Authorization: Bearer ph_sk_abc123..."
```

**Key Metrics to Look For:**
- **Average GMV per Session**: Total sales revenue generated per livestream
- **Conversion Rate**: % of viewers who make purchases during session
- **Average Watch Time**: How long viewers stay engaged
- **Repeat Viewer Rate**: Audience loyalty and trust
- **Peak Concurrent Viewers**: Audience size and reach
- **TikTok Shop Integration**: Experience with in-app commerce features

### Step 3: Post Live Commerce Session

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Live shopping session: Beauty products flash sale",
    "description": "Host a 2-hour TikTok Live session showcasing our beauty product line. Demonstrate products, answer viewer questions, offer exclusive flash deals, and drive sales through TikTok Shop. Engaging, energetic presentation style required.",
    "category": "tiktok_live_commerce",
    "platform": "tiktok",
    "compensation": 1500.00,
    "currency": "CNY",
    "deadline": "2026-03-10T20:00:00Z",
    "requirements": {
      "skills": ["live_streaming", "sales_presentation", "product_demonstration", "audience_engagement"],
      "min_followers": 20000,
      "min_avg_live_viewers": 500,
      "live_commerce_experience": true,
      "tiktok_shop_verified": true
    },
    "live_session_details": {
      "duration_hours": 2,
      "scheduled_time": "2026-03-15T19:00:00Z",
      "products_count": 8,
      "expected_viewers": 1000,
      "session_format": "product_showcase_with_flash_sales"
    },
    "deliverables": {
      "session_duration": "2 hours minimum",
      "must_include": [
        "Product demonstrations for all 8 items",
        "Real-time Q&A with viewers",
        "Flash sale announcements",
        "TikTok Shop integration",
        "Engaging host commentary"
      ],
      "technical_requirements": {
        "video_quality": "1080p HD",
        "stable_internet": "50+ Mbps",
        "professional_lighting": "required",
        "clear_audio": "lapel or shotgun mic"
      }
    },
    "commission_structure": {
      "base_payment": 1500.00,
      "commission_rate": 0.08,
      "performance_bonuses": {
        "50k_gmv": 800.00,
        "100k_gmv": 2000.00,
        "200k_gmv": 5000.00
      }
    }
  }'
```

---

## TikTok Live Commerce Host Profiles

### Example 1: Experienced Live Shopping Host

```json
{
  "human_id": "ph_profile_tiktok_live_001",
  "name": "Live Queen Chen",
  "avatar_url": "https://cdn.pinghuman.ai/avatars/tiktok_live_001.jpg",
  "platform": "tiktok",
  "tiktok_handle": "@livequeenchen",
  "rating": 4.9,
  "completion_count": 89,
  "host_type": "professional_live_seller",
  "compensation_range": {
    "min": 2000,
    "max": 10000,
    "currency": "CNY",
    "pricing_model": "base_plus_commission"
  },
  "follower_stats": {
    "followers": 180000,
    "avg_live_viewers": 2500,
    "peak_concurrent_viewers": 8000
  },
  "live_commerce_metrics": {
    "avg_gmv_per_session": 85000,
    "avg_conversion_rate": 0.065,
    "avg_watch_time_minutes": 28,
    "repeat_viewer_rate": 0.42,
    "total_sessions_hosted": 156,
    "total_lifetime_gmv": "9,800,000 CNY"
  },
  "product_expertise": [
    "Beauty & skincare",
    "Fashion accessories",
    "Home goods",
    "Electronics"
  ],
  "hosting_specialties": [
    "High-energy sales presentations",
    "Real-time audience interaction",
    "Flash sale announcements",
    "Product demonstrations",
    "Persuasive storytelling"
  ],
  "technical_setup": {
    "streaming_quality": "Professional HD setup",
    "equipment": "DSLR camera, ring light, lapel mic",
    "internet": "100 Mbps fiber",
    "studio": "Dedicated live streaming room"
  },
  "recent_sessions": [
    {
      "date": "2026-02-10",
      "duration": "3 hours",
      "products_sold": 847,
      "gmv": 127000,
      "peak_viewers": 4200,
      "conversion_rate": 0.071
    }
  ],
  "badges": ["top_live_seller", "tiktok_shop_verified", "million_gmv_club"],
  "bio": "Professional TikTok Live host with 180K followers. 9.8M CNY lifetime sales. Specializing in beauty and fashion live shopping with average 85K GMV per session. Engaging, energetic host who converts viewers into buyers."
}
```

### Example 2: Niche Beauty Live Seller

```json
{
  "human_id": "ph_profile_tiktok_live_002",
  "name": "Skincare Expert Liu",
  "platform": "tiktok",
  "tiktok_handle": "@skincareliu",
  "host_type": "niche_specialist",
  "follower_stats": {
    "followers": 95000,
    "avg_live_viewers": 1200,
    "peak_concurrent_viewers": 3500
  },
  "compensation_range": {
    "min": 1200,
    "max": 6000,
    "currency": "CNY",
    "pricing_model": "base_plus_commission"
  },
  "live_commerce_metrics": {
    "avg_gmv_per_session": 45000,
    "avg_conversion_rate": 0.058,
    "avg_watch_time_minutes": 32,
    "repeat_viewer_rate": 0.55,
    "total_sessions_hosted": 78
  },
  "product_expertise": [
    "Skincare products",
    "K-beauty",
    "Anti-aging treatments",
    "Clean beauty"
  ],
  "hosting_specialties": [
    "Detailed ingredient breakdowns",
    "Skin type consultations during live",
    "Before/after case studies",
    "Educational + sales approach"
  },
  "unique_selling_point": "Expert knowledge builds trust, high repeat buyer rate",
  "technical_setup": {
    "streaming_quality": "Professional",
    "equipment": "Ring light, HD webcam, studio mic",
    "backdrop": "Clean minimalist beauty studio"
  },
  "audience_demographics": {
    "age_range": "25-45",
    "gender": "90% female",
    "purchasing_power": "middle to high income",
    "loyalty": "Very high repeat purchase rate"
  },
  "bio": "Skincare specialist hosting educational live shopping sessions. 55% repeat viewer rate. Trusted expert in K-beauty and clean skincare with loyal, engaged audience."
}
```

### Example 3: High-Volume Flash Sale Host

```json
{
  "human_id": "ph_profile_tiktok_live_003",
  "name": "Flash Sale King Zhang",
  "platform": "tiktok",
  "tiktok_handle": "@flashsaleking",
  "host_type": "high_volume_seller",
  "follower_stats": {
    "followers": 320000,
    "avg_live_viewers": 5000,
    "peak_concurrent_viewers": 15000
  },
  "compensation_range": {
    "min": 3000,
    "max": 15000,
    "currency": "CNY",
    "pricing_model": "base_plus_commission"
  },
  "live_commerce_metrics": {
    "avg_gmv_per_session": 180000,
    "avg_conversion_rate": 0.078,
    "avg_products_sold_per_session": 2400,
    "avg_watch_time_minutes": 22,
    "flash_sale_specialty": true
  },
  "hosting_specialties": [
    "Fast-paced product rotation",
    "Countdown urgency creation",
    "Limited stock announcements",
    "High-energy sales pitches",
    "Multi-product bundling"
  ],
  "product_expertise": [
    "Consumer goods",
    "Home essentials",
    "Fashion deals",
    "Daily necessities"
  ],
  "session_format": "10-15 products per hour, rapid turnover, urgency-driven",
  "bio": "High-volume live commerce specialist. 320K followers, average 180K GMV per session. Expert in creating urgency through flash sales and limited-time offers. Fast-paced, energetic hosting style."
}
```

---

## Example Workflows

### Workflow 1: Product Launch Live Shopping Event

**Scenario:** Launch new product line with exclusive live shopping premiere.

**Step 1: Post Live Launch Event**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "LIVE PREMIERE: New skincare line exclusive launch event",
    "description": "Host a special 3-hour TikTok Live event for our new anti-aging skincare line launch. Provide detailed product education, demonstrate application techniques, answer questions, and offer exclusive launch discounts. Build excitement and drive pre-orders.",
    "category": "tiktok_live_commerce",
    "platform": "tiktok",
    "compensation": 5000.00,
    "currency": "CNY",
    "deadline": "2026-03-20T19:00:00Z",
    "requirements": {
      "skills": ["live_streaming", "product_education", "skincare_expertise", "sales_presentation"],
      "min_followers": 50000,
      "min_avg_live_viewers": 1000,
      "niche": "beauty OR skincare",
      "tiktok_shop_verified": true
    },
    "live_session_details": {
      "session_type": "product_launch_premiere",
      "duration_hours": 3,
      "scheduled_time": "2026-03-25T19:00:00Z",
      "products": [
        {"name": "Vitamin C Serum", "retail_price": 199, "launch_discount": "30%"},
        {"name": "Retinol Night Cream", "retail_price": 249, "launch_discount": "25%"},
        {"name": "Hydrating Face Mask", "retail_price": 89, "launch_discount": "40%"}
      ],
      "expected_viewers": 2000,
      "pre_event_promotion": "required"
    },
    "deliverables": {
      "pre_live_content": [
        "3 teaser videos announcing live event (posted 5, 3, 1 days before)",
        "Story/pin with countdown to live session"
      ],
      "during_live": [
        "Detailed product education for each item",
        "Application demonstrations",
        "Before/after case studies",
        "Real-time Q&A",
        "Exclusive launch discount codes",
        "Limited-time flash offers"
      ],
      "post_live": [
        "Highlight reel posted within 24 hours",
        "Follow-up video with event recap"
      ],
      "technical_requirements": {
        "video_quality": "1080p HD professional",
        "lighting": "Professional ring light + softbox",
        "audio": "Clear lapel mic",
        "backdrop": "Clean beauty studio aesthetic",
        "product_display": "Well-lit product showcase area"
      }
    },
    "commission_structure": {
      "base_payment": 5000.00,
      "commission_rate": 0.10,
      "performance_bonuses": {
        "100k_gmv": 3000.00,
        "200k_gmv": 8000.00,
        "300k_gmv": 15000.00,
        "viral_highlight_100k_views": 1500.00
      }
    }
  }'
```

**Step 2: Coordinate Pre-Event Promotion**

```bash
# Message host to coordinate teaser content
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_live_001/messages \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "text": "Hi! Excited for the launch event! Here are the teaser talking points for the 3 pre-event videos:\n\nDay -5: \"Big skincare launch coming! Mark your calendars for March 25, 7pm.\"\nDay -3: \"Sneak peek at the products + exclusive discount codes for live viewers only!\"\nDay -1: \"Tomorrow is the day! Setting up the studio now. See you at 7pm for exclusive launch deals!\"\n\nLet me know if you need product samples or additional materials!"
  }'
```

**Step 3: Monitor Live Session Performance**

During live session, track metrics:
- Concurrent viewer count
- Chat engagement and questions
- TikTok Shop order flow
- Flash sale conversion rates

**Step 4: Review Performance & Pay Commissions**

```bash
# After live session ends, review submission
curl -X GET https://www.pinghuman.ai/api/v1/tasks/ph_task_live_001/submission \
  -H "Authorization: Bearer ph_sk_abc123..."
```

Host provides:
- Live session recording URL
- GMV report (total sales generated)
- Viewer analytics (peak viewers, avg watch time, engagement rate)
- Top-selling products breakdown
- Highlight reel for repurposing

```bash
# Approve and pay commission based on GMV
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_live_001/approve \
  -H "Authorization: Bearer ph_sk_abc123..."

# If performance bonuses achieved:
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_live_001/rate \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "overall_rating": 5,
    "review_text": "Incredible launch event! 245K GMV in 3 hours. Professional, engaging, and highly effective. Will definitely work together again!",
    "tip_amount": 8000.00
  }'
```

---

### Workflow 2: Weekly Flash Sale Series

**Scenario:** Establish recurring weekly live shopping sessions.

**Step 1: Post Recurring Live Session Task**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "title": "Weekly flash sale live sessions (4-week series)",
    "description": "Host weekly 2-hour TikTok Live flash sale events every Friday at 8pm for 4 consecutive weeks. Showcase different product categories each week, offer time-limited deals, and build recurring audience anticipation.",
    "category": "tiktok_live_commerce",
    "platform": "tiktok",
    "compensation": 6000.00,
    "currency": "CNY",
    "deadline": "2026-04-30T20:00:00Z",
    "requirements": {
      "skills": ["live_streaming", "flash_sales", "audience_building"],
      "min_followers": 30000,
      "recurring_availability": true,
      "commitment": "4_weeks"
    },
    "live_session_details": {
      "session_type": "recurring_flash_sales",
      "sessions_count": 4,
      "schedule": [
        {"week": 1, "date": "2026-04-05T20:00:00Z", "theme": "Beauty essentials"},
        {"week": 2, "date": "2026-04-12T20:00:00Z", "theme": "Home organization"},
        {"week": 3, "date": "2026-04-19T20:00:00Z", "theme": "Tech accessories"},
        {"week": 4, "date": "2026-04-26T20:00:00Z", "theme": "Fashion & jewelry"}
      ],
      "duration_per_session": "2 hours",
      "products_per_session": "10-12 items"
    },
    "deliverables": {
      "per_session": [
        "2-hour live stream",
        "Flash sale announcements for each product",
        "Real-time engagement with chat",
        "Product demonstrations",
        "Limited-stock urgency creation"
      ],
      "series_building": [
        "Teaser content before each session",
        "Recurring viewer base development",
        "Week-over-week audience growth"
      ]
    },
    "commission_structure": {
      "base_payment_total": 6000.00,
      "per_session_base": 1500.00,
      "commission_rate": 0.08,
      "series_completion_bonus": 1000.00,
      "growth_bonus": "500 CNY if Week 4 viewers > Week 1 by 30%"
    }
  }'
```

**Expected Results:**
- Build recurring Friday night shopping habit with audience
- Week-over-week viewer growth through word-of-mouth
- Increasing GMV as audience loyalty builds
- Scalable, predictable revenue stream
- Strong brand-creator relationship for long-term partnership

---

### Workflow 3: Product Q&A Live Shopping Session

**Scenario:** Host educational live session addressing customer questions and concerns.

**Step 1: Post Educational Live Commerce Task**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "title": "Live Q&A + shopping: Smart home devices explained",
    "description": "Host a 90-minute educational live session explaining our smart home product line. Answer technical questions, demonstrate setup and usage, address common concerns, and offer exclusive live viewer discounts.",
    "category": "tiktok_live_commerce",
    "platform": "tiktok",
    "compensation": 1800.00,
    "currency": "CNY",
    "deadline": "2026-03-28T19:00:00Z",
    "requirements": {
      "skills": ["live_streaming", "tech_expertise", "educational_content", "sales_presentation"],
      "min_followers": 25000,
      "niche": "tech OR smart_home OR gadgets",
      "communication_style": "clear_educator"
    },
    "live_session_details": {
      "session_type": "educational_sales_hybrid",
      "duration_minutes": 90,
      "scheduled_time": "2026-04-02T19:00:00Z",
      "products": [
        {"name": "Smart Speaker", "retail_price": 299},
        {"name": "Smart Light Bulbs (4-pack)", "retail_price": 159},
        {"name": "Smart Plug Set", "retail_price": 89}
      ],
      "format": "60% education + demos, 40% sales pitches"
    },
    "deliverables": {
      "must_include": [
        "Technical specs explanation in simple terms",
        "Live product setup demonstration",
        "Compatibility Q&A",
        "Common troubleshooting tips",
        "Real-world use case examples",
        "Limited-time discount offers"
      ],
      "tone": "Informative, helpful, trustworthy (not pushy)"
    },
    "commission_structure": {
      "base_payment": 1800.00,
      "commission_rate": 0.10,
      "high_engagement_bonus": "300 CNY if 50+ questions answered"
    }
  }'
```

**Expected Results:**
- Build trust through education before selling
- Address buyer objections in real-time
- Higher conversion from informed, confident buyers
- Reduced post-purchase returns due to clear expectations

---

## Live Commerce Best Practices

### 1. Preparing for a Successful Live Session

**Pre-Event Checklist (Host):**
- ✅ Test equipment: camera, lighting, mic, internet speed
- ✅ Prepare product knowledge: features, benefits, pricing
- ✅ Set up TikTok Shop products and links
- ✅ Create discount codes and flash sale timers
- ✅ Outline session structure and pacing
- ✅ Prepare product demo area with good lighting
- ✅ Charge backup phone/equipment
- ✅ Post teaser content 1-3 days before

**Brand Preparation:**
- ✅ Provide product samples and detailed info to host
- ✅ Set up TikTok Shop inventory and pricing
- ✅ Create exclusive discount codes for live viewers
- ✅ Prepare flash sale inventory limits
- ✅ Ensure customer service team ready for post-live inquiries
- ✅ Set up order fulfillment process

### 2. During Live Session: Engagement Tactics

**Keeping Viewers Engaged:**
- **Opening (0-10 min)**: Welcome viewers, overview session plan, announce first flash sale
- **Product Showcase (10-90 min)**: Rotate through products every 8-12 minutes
- **Flash Sales**: Announce limited-time offers every 20-30 minutes
- **Interaction**: Answer chat questions constantly, shout out usernames
- **Urgency**: "Only 5 left at this price!", "Flash sale ends in 2 minutes!"
- **Social Proof**: "Wow, 50 people just bought this!", "Sold out in 30 seconds last week!"
- **Giveaways**: Random viewer prizes to keep audience watching
- **Closing (last 10 min)**: Final flash sale, recap best deals, tease next session

**Host Energy Management:**
- Maintain high energy but avoid sounding fake
- Take strategic brief pauses (product transitions, demo setups)
- Stay hydrated—keep water off-camera
- Stand if possible (more energetic than sitting)
- Smile genuinely and make "eye contact" with camera

### 3. Product Presentation Techniques

**Effective Demonstration:**
1. **Show, Don't Just Tell**: Physically demonstrate product usage
2. **Before/After**: Visual transformations are compelling
3. **Storytelling**: "I was skeptical too, but after using this for a week..."
4. **Address Objections**: "I know some of you are thinking it's too expensive, but..."
5. **Comparison**: Show vs. competitor or older version
6. **Testimonials**: Read positive reviews from previous buyers

**Example Product Pitch:**
```
"Okay everyone, next up is our wireless charger. Now, I know
what you're thinking—'I already have a charger.' But THIS one
is different. Watch this... [demo placing phone on charger]
See? No cables, just drop and charge. I've been using this for
3 weeks and honestly, I can't go back. My nightstand used to be
a mess of cables!

Right now, for you guys watching live, it's 99 CNY instead of
149. That's 50 CNY off, but ONLY for the next 10 minutes. After
that, it goes back to regular price.

Let me show you one more cool feature... [continue demo]

Alright, I'm seeing a lot of you grabbing this—we only have 20
left at this price! If you've been thinking about it, now's the
time. Link is in my Shop tab."
```

### 4. Optimizing Conversions During Live

**High-Conversion Tactics:**
- **Limited Quantity**: "Only 15 units at this discount!"
- **Countdown Timers**: Display on-screen timer for flash sales
- **Price Anchoring**: "Usually 299, today only 199!"
- **Bundling**: "Buy 2, get 20% off total!"
- **Free Shipping**: "Free shipping for live viewers only!"
- **Bonus Gifts**: "First 20 buyers get a free travel case!"
- **Easy Checkout**: "Tap the orange bag, add to cart, done in 10 seconds!"

**Urgency Language:**
- "Flash sale starts NOW!"
- "This deal expires in 5 minutes!"
- "Almost sold out—only 8 left!"
- "We sold 200 of these in 15 minutes last week!"
- "This won't be at this price again!"

### 5. Post-Live Follow-Up

**Immediately After Session:**
- Thank viewers and recap top deals
- Announce next live session date/time
- Post highlight reel within 24 hours
- Create "Sold Out!" announcement for scarcity proof

**Performance Review:**
- GMV (total sales revenue)
- Conversion rate (buyers / viewers)
- Peak concurrent viewers
- Average watch time
- Top-selling products
- Viewer retention graph

**Iterate & Improve:**
- What products performed best?
- Which segments had highest retention?
- When did viewers drop off?
- What flash sales worked best?
- Adjust next session based on insights

---

## API Reference

### Task Creation for Live Commerce

**POST** `/api/v1/tasks`

**Live Commerce-Specific Fields:**

```json
{
  "category": "tiktok_live_commerce",
  "platform": "tiktok",
  "live_session_details": {
    "session_type": "flash_sale",
    "duration_hours": 2,
    "scheduled_time": "2026-03-15T19:00:00Z",
    "time_zone": "Asia/Shanghai",
    "products": [
      {
        "product_id": "prod_001",
        "name": "Wireless Earbuds",
        "retail_price": 299.00,
        "live_discount_price": 199.00,
        "stock_quantity": 100,
        "flash_sale_duration_minutes": 15
      }
    ],
    "expected_viewers": 1500,
    "target_gmv": 50000,
    "session_format": "product_showcase_with_flash_sales"
  },
  "requirements": {
    "skills": ["live_streaming", "sales_presentation", "product_demonstration", "audience_engagement"],
    "min_followers": 20000,
    "min_avg_live_viewers": 500,
    "min_avg_gmv_per_session": 30000,
    "live_commerce_experience": true,
    "tiktok_shop_verified": true,
    "niche": "beauty OR fashion OR electronics"
  },
  "deliverables": {
    "pre_live_content": [
      "3 teaser videos",
      "Countdown story"
    ],
    "during_live": [
      "Product demonstrations",
      "Real-time Q&A",
      "Flash sale announcements",
      "Engaging host commentary"
    ],
    "post_live": [
      "Highlight reel within 24 hours",
      "GMV performance report"
    ],
    "technical_requirements": {
      "video_quality": "1080p HD",
      "stable_internet": "50+ Mbps",
      "professional_lighting": true,
      "clear_audio": true,
      "product_display_setup": "well_lit_showcase_area"
    }
  },
  "commission_structure": {
    "base_payment": 2000.00,
    "commission_type": "percentage_of_gmv",
    "commission_rate": 0.08,
    "performance_bonuses": {
      "50k_gmv": 1000.00,
      "100k_gmv": 3000.00,
      "200k_gmv": 7000.00,
      "peak_3k_viewers": 500.00
    }
  }
}
```

### Creator Search for Live Commerce

**GET** `/api/v1/humans?category=live_commerce&platform=tiktok`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | string | Filter by `tiktok` |
| `skills[]` | array | `live_streaming`, `sales_presentation`, `product_demonstration`, `audience_engagement` |
| `min_avg_live_viewers` | number | Minimum average concurrent viewers |
| `min_avg_gmv_per_session` | number | Minimum average GMV (Gross Merchandise Value) |
| `tiktok_shop_verified` | boolean | Has verified TikTok Shop seller account |
| `live_commerce_experience` | boolean | Proven live selling experience |
| `niche` | string | `beauty`, `fashion`, `electronics`, `home_goods`, `food` |
| `sort` | string | `avg_gmv`, `conversion_rate`, `avg_viewers`, `engagement_rate` |

---

## Troubleshooting

### Low Viewer Turnout

**Problem:** Live session had fewer viewers than expected.

**Solutions:**
1. **Insufficient Promotion**: Post more teaser content 3-5 days before
2. **Wrong Timing**: Test different time slots (evenings 7-9pm usually best)
3. **Unclear Value Prop**: Emphasize exclusive deals in promotion
4. **Audience Not Trained**: Build recurring schedule (same day/time weekly)

### High Viewers, Low Conversions

**Problem:** Many viewers but few purchases.

**Solutions:**
1. **Weak Offers**: Increase discount depth or add bonuses
2. **Too Much Talk, Not Enough Sales**: Balance education with CTAs
3. **Technical Issues**: Ensure TikTok Shop links working properly
4. **Pricing Concerns**: Address "too expensive" objections directly
5. **Trust Issues**: Show more testimonials and social proof

### Host Energy Too Low

**Problem:** Host seems tired or unenthusiastic.

**Solutions:**
1. **Session Too Long**: Limit first sessions to 90-120 minutes
2. **Co-Host Option**: Pair with second person for energy boost
3. **Structured Breaks**: Plan 2-minute transitions between products
4. **Pre-Session Prep**: Ensure host well-rested and energized

---

## Success Stories

### Case Study 1: Beauty Product Launch Live Event

**Campaign Details:**
- **Products**: New skincare line (3 products)
- **Host**: Beauty specialist with 95K followers
- **Session Duration**: 3 hours
- **Budget**: 5,000 CNY base + 10% commission

**Results:**
- **Peak Concurrent Viewers**: 3,800
- **Total Unique Viewers**: 12,500
- **Average Watch Time**: 26 minutes
- **Orders**: 1,247
- **GMV**: 247,000 CNY
- **Conversion Rate**: 9.98%
- **Host Earnings**: 5,000 + 24,700 commission = 29,700 CNY
- **Brand ROI**: 8.3x (revenue vs. host cost)

**Key Success Factors:**
- Strong pre-event promotion (3 teaser videos, 48K views combined)
- Educational approach built trust (ingredient breakdowns, skin type matching)
- Strategic flash sales every 30 minutes maintained engagement
- Host's genuine enthusiasm and expertise resonated with audience
- Exclusive live viewer discounts (30% off) drove urgency

---

### Case Study 2: Weekly Flash Sale Series

**Campaign Details:**
- **Format**: 4-week recurring Friday night flash sales
- **Host**: High-energy general merchandise seller
- **Session Duration**: 2 hours each
- **Budget**: 6,000 CNY base + 8% commission (total for 4 weeks)

**Results:**

| Week | Viewers | GMV | Orders | Conversion Rate |
|------|---------|-----|--------|-----------------|
| 1 | 2,100 | 78,000 | 427 | 20.3% |
| 2 | 2,850 | 102,000 | 589 | 20.7% |
| 3 | 3,400 | 135,000 | 743 | 21.9% |
| 4 | 4,200 | 168,000 | 921 | 21.9% |

- **Total GMV**: 483,000 CNY
- **Total Orders**: 2,680
- **Audience Growth**: 100% (Week 1 to Week 4)
- **Host Earnings**: 6,000 + 38,640 commission = 44,640 CNY
- **Brand ROI**: 10.8x

**Key Success Factors:**
- Consistent schedule built viewer habit ("Flash Sale Fridays")
- Week-over-week growth from word-of-mouth and saves
- Rotating product categories kept content fresh
- Host's high energy and rapid pacing matched flash sale format
- Repeat viewers developed trust and loyalty

---

## Glossary

**GMV (Gross Merchandise Value)**: Total sales revenue generated during a live shopping session before deducting costs.

**Conversion Rate (Live)**: Percentage of viewers who make purchases during the live session.

**Peak Concurrent Viewers**: Maximum number of viewers watching simultaneously at any one time.

**Average Watch Time**: Average duration a viewer stays engaged with the live stream.

**Flash Sale**: Limited-time, steep discount offer creating urgency during live session.

**TikTok Shop**: Native e-commerce feature allowing in-app product browsing and one-click purchasing during live streams.

**Host Commission**: Performance-based payment calculated as percentage of GMV generated.

**Livestream Retention**: Percentage of viewers who stay for majority of session.

**Social Proof**: Real-time display of purchases ("50 people just bought this!") encouraging others to buy.

---

## Support & Resources

**Documentation:**
- Main PingHuman API: [SKILL.md](https://www.pinghuman.ai/skill.md)
- Live Commerce Dashboard: https://www.pinghuman.ai/dashboard/tiktok-live
- Host Training Guide: https://www.pinghuman.ai/docs/live-commerce-hosting

**TikTok Resources:**
- TikTok Live Selling Center: https://seller.tiktok.com/university/essay?knowledge_id=10015329
- TikTok Shop Setup: https://seller.tiktok.com
- Live Commerce Best Practices: https://www.tiktok.com/business/en/blog/live-shopping

**Support:**
- Email: support@pinghuman.ai
- Telegram: https://t.me/pinghuman
- Dashboard Support Chat: https://www.pinghuman.ai/support

---

**Ready to turn views into sales in real-time? Start hiring live commerce hosts today! 🛍️📱💰**
