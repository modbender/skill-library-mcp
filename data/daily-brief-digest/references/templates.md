# Daily Digest Templates

Use these patterns to maintain a high-quality, efficient output.

## Summary Pattern (Markdown)

```markdown
**📅 Daily Briefing - {{date}}**

**📧 Emails (Recent)**
{% for email in emails %}
- **{{email.from.name or email.from.addr}}**: {{email.subject}} ({{email.date}})
{% endfor %}

**🗓️ Calendar**
{{calendar_summary}}

**📰 News**
{% for item in news %}
- {{item.title}} ({{item.url}})
{% endfor %}
```
