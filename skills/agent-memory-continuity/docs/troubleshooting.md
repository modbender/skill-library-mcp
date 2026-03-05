# Agent Memory Continuity - Troubleshooting Guide

## Common Issues and Solutions

### Issue: "Memory search not working"
**Solution:** Ensure `memory_search` function is available in your OpenClaw environment.

### Issue: "Memory files not syncing"
**Solution:** 
1. Check if cron is running: `systemctl status cron`
2. Verify cron job: `crontab -l | grep memory`
3. Check sync log: `cat .memory-sync-log`

### Issue: "Daily memory file not created"
**Solution:**
1. Run: `bash scripts/init-memory-protocol.sh`
2. Manually create: `cp templates/daily-memory-template.md memory/$(date +%Y-%m-%d).md`

### Issue: "Configuration files missing"
**Solution:**
1. Re-run installation: `bash install.sh`
2. Check file permissions in config/ directory

### Issue: "Memory continuity not working across sessions"
**Solution:**
1. Verify AGENT_MEMORY_PROTOCOL.md exists in workspace
2. Ensure agent follows search-first protocol
3. Check memory directory has proper write permissions

## Support

For enterprise support and consulting:
- **Email:** support@sapconet.co.za
- **Phone:** +27 (0)53 123 4567
- **Web:** https://sapconet.co.za

## Version Information
- **Version:** 1.0.0
- **Last Updated:** 2026-02-15
- **Compatible with:** OpenClaw 1.0+