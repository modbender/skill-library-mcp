# Quick Start Guide - CTF Writeup Generator

Get up and running in 5 minutes!

## For Users

### Installation (30 seconds)

```bash
# Install the ClawHub CLI
npm install -g clawhub

# Install this skill
clawhub install ctf-writeup-generator

# Verify installation
openclaw skills list | grep ctf-writeup
```

### First Writeup (2 minutes)

Just talk to your OpenClaw agent:

```
You: "I just solved a web exploitation challenge called SQL Injection 101 from 
      HackTheBox. I used sqlmap to extract the database and found the flag 
      HTB{sql_1nj3ct10n_m4st3r}. Can you generate a writeup?"

OpenClaw: [Asks for details about tools and steps]

You: "I used Burp Suite to intercept requests, found a vulnerable login form, 
      then ran sqlmap with the -u flag pointing to login.php. It extracted 
      the users table and I found the flag in the admin account."

OpenClaw: [Generates professional writeup and saves to 
          hackthebox_sql-injection-101_writeup.md]
```

### View Your Writeup

```bash
# The writeup is saved in your current directory
cat hackthebox_sql-injection-101_writeup.md

# Or open in your editor
code hackthebox_sql-injection-101_writeup.md
```

## For Publishers

### Publishing Your Skill (3 minutes)

```bash
# 1. Login to ClawHub
clawhub login

# 2. Navigate to skill directory
cd ctf-writeup-generator

# 3. Publish!
clawhub publish . \
  --slug ctf-writeup-generator \
  --name "CTF Writeup Generator" \
  --version 1.0.0 \
  --changelog "Initial release with multi-platform support"

# 4. View your published skill
# Visit: https://clawhub.ai/skills/YOUR-USERNAME/ctf-writeup-generator
```

## Common Use Cases

### 1. Document a Pwn Challenge

```
"Generate a writeup for the buffer overflow challenge 'Stack Smasher' from 
 PicoCTF. I used gdb, pwntools, and found the flag picoCTF{buff3r_pwn3d}."
```

### 2. Multiple Challenges at Once

```
"Create writeups for all three forensics challenges I solved today from the 
 Shaastra CTF: 'Hidden Files', 'Memory Dump', and 'Network Capture'."
```

### 3. Different Formats

```
"Generate a tutorial-style writeup for beginners for this crypto challenge."
"Create a speedrun writeup with just the essential steps."
"Make a portfolio-ready writeup I can add to my GitHub."
```

### 4. Export to PDF

```
"Generate a writeup and export it to PDF format."
```

## Configuration (Optional)

Add to your shell config for personalization:

```bash
# ~/.bashrc or ~/.zshrc
export CTF_AUTHOR="akm626"
export CTF_PLATFORM="HackTheBox"
export CTF_WRITEUP_STYLE="tutorial"
```

Restart your shell or run `source ~/.bashrc`

## Troubleshooting

### Skill not working?

```bash
# Check if skill is installed
openclaw skills list

# Reinstall if needed
clawhub update ctf-writeup-generator

# Check OpenClaw logs
tail -f ~/.openclaw/logs/agent.log
```

### Flag format not detected?

```
"The flag format is CUSTOM{...} with case-sensitive content."
```

### Wrong category assigned?

```
"This is a reverse engineering challenge, not web exploitation."
```

## Tips for Best Results

1. **Be specific**: Include exact commands and tool names
2. **Include context**: Platform, difficulty, points
3. **Mention dead-ends**: What didn't work helps learning
4. **Add insights**: Your unique approach matters

## Examples

See `example_writeup.md` for a full example of generated output.

## Next Steps

- Read `README.md` for full documentation
- Check `PUBLISHING.md` to publish your own skill
- Join OpenClaw Discord for community support

## Support

- **Issues**: https://github.com/yourusername/ctf-writeup-generator/issues
- **Discord**: OpenClaw community #skill-support
- **Email**: your-email@example.com

---

**Happy hacking and writing!** 🎯🔒📝
