# Kit Personalization Tags Reference

**For the Kit Email Marketing Operator**

Use these Liquid tags in your email content to personalize for each subscriber.

---

## Basic Subscriber Fields

### Name Fields
```liquid
{{ subscriber.first_name }}          # First name
{{ subscriber.last_name }}           # Last name (if collected)
{{ subscriber.name }}                # Full name
```

**Usage:**
```
Hey {{ subscriber.first_name }},

Welcome to the list!
```

**Fallback (if no name):**
```liquid
{% if subscriber.first_name %}
  Hey {{ subscriber.first_name }},
{% else %}
  Hey friend,
{% endif %}
```

### Contact Info
```liquid
{{ subscriber.email_address }}       # Email address
{{ subscriber.id }}                  # Subscriber ID
{{ subscriber.created_at }}          # Subscription date
```

### State
```liquid
{{ subscriber.state }}               # active, bounced, complained, unsubscribed
```

---

## Custom Fields

If you've created custom fields in Kit, reference them like this:

```liquid
{{ subscriber.FIELD_NAME }}
```

**Common custom fields:**
```liquid
{{ subscriber.company }}
{{ subscriber.website }}
{{ subscriber.job_title }}
{{ subscriber.phone }}
{{ subscriber.city }}
{{ subscriber.country }}
{{ subscriber.industry }}
```

**Check available custom fields:**
Use the Kit API: `kit.listCustomFields()`

---

## Conditional Logic

### If/Else
```liquid
{% if subscriber.first_name %}
  Welcome back, {{ subscriber.first_name }}!
{% else %}
  Welcome back!
{% endif %}
```

### Multiple Conditions
```liquid
{% if subscriber.plan == "premium" %}
  Here's your premium content:
{% elsif subscriber.plan == "basic" %}
  Upgrade to premium for access:
{% else %}
  Join our community:
{% endif %}
```

### Check for Empty
```liquid
{% unless subscriber.company %}
  What company do you work for? [Reply and let me know]
{% endunless %}
```

---

## Unsubscribe Links

**Required by law (CAN-SPAM):**
```liquid
{{ unsubscribe_url }}                # Standard unsubscribe link
```

**Formatted example:**
```html
<p style="font-size: 12px; color: #666;">
  Don't want these emails? <a href="{{ unsubscribe_url }}">Unsubscribe</a>
</p>
```

---

## View in Browser Link

```liquid
{{ browser_url }}                    # "View in browser" link
```

**Usage:**
```html
<p>Can't see this email? <a href="{{ browser_url }}">View in browser</a></p>
```

---

## Tags & Segments

**Check if subscriber has a tag:**
```liquid
{% if subscriber.tags contains "premium" %}
  Premium-only content here
{% endif %}
```

**List all tags:**
```liquid
{{ subscriber.tags | join: ", " }}  # Shows all tags as comma-separated list
```

---

## Date Formatting

```liquid
{{ subscriber.created_at | date: "%B %d, %Y" }}  # February 17, 2026
{{ subscriber.created_at | date: "%m/%d/%Y" }}   # 02/17/2026
```

---

## Personalization Best Practices

### 1. Always Use Fallbacks
❌ **Bad:**
```
Hey {{ subscriber.first_name }},
```
If no name → "Hey ,"

✅ **Good:**
```
{% if subscriber.first_name %}
  Hey {{ subscriber.first_name }},
{% else %}
  Hey there,
{% endif %}
```

### 2. Test Before Sending
Send test email to yourself, check:
- Name displays correctly
- Custom fields populate
- Fallbacks work
- Unsubscribe link works

### 3. Don't Overdo It
❌ **Bad:**
```
Hey {{ subscriber.first_name }}, I know you work at {{ subscriber.company }}
in {{ subscriber.city }} as a {{ subscriber.job_title }}, so here's...
```
Feels creepy.

✅ **Good:**
```
Hey {{ subscriber.first_name }},

Quick thought for {{ subscriber.job_title }}s like you...
```
Natural and relevant.

### 4. Segment for Deeper Personalization
Instead of complex conditionals, send different emails to different segments.

---

## Example: Fully Personalized Welcome Email

```liquid
Subject: Welcome to [Your List], {{ subscriber.first_name | default: "friend" }}!

---

{% if subscriber.first_name %}
Hey {{ subscriber.first_name }},
{% else %}
Hey there,
{% endif %}

Thanks for joining! You subscribed on {{ subscriber.created_at | date: "%B %d, %Y" }}.

Here's what you can expect:
- Weekly tips on [your niche]
- No spam, no BS
- Unsubscribe anytime (but I hope you stay)

{% if subscriber.company %}
  Since you're with {{ subscriber.company }}, I think you'll especially enjoy our content on [relevant topic].
{% endif %}

Your first resource:
[Link to valuable content]

Talk soon,
[Your Name]

---

P.S. - Hit reply anytime. I read every email.

<p style="font-size: 11px; color: #999;">
  Don't want these emails? <a href="{{ unsubscribe_url }}" style="color: #999;">Unsubscribe</a>
</p>
```

---

## Common Mistakes

❌ **Missing fallback for first_name**
→ Results in "Hey ," if name not provided

❌ **Using custom fields without checking they exist**
→ Displays blank or "null"

❌ **Forgetting unsubscribe link**
→ Violates CAN-SPAM, damages deliverability

❌ **Over-personalizing**
→ Feels creepy, not helpful

❌ **Not testing**
→ Broken tags go out to thousands

---

## Testing Checklist

Before sending, test:
- [ ] First name displays (or fallback works)
- [ ] Custom fields populate correctly
- [ ] Conditional logic works as expected
- [ ] Unsubscribe link is present and functional
- [ ] View in browser link works
- [ ] No broken tags ({{ }} showing in email)
- [ ] Displays correctly on mobile

---

**Use personalization wisely. Make it feel human, not robotic.**
