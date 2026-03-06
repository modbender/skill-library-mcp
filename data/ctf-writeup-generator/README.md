# CTF Writeup Generator - OpenClaw Skill

A professional skill for OpenClaw that automatically generates structured CTF writeups from solving sessions.

## Features

- 🎯 **Automatic Flag Detection**: Recognizes common CTF flag formats (CTF{}, HTB{}, SHAASTRA{}, etc.)
- 📂 **Smart Categorization**: Auto-categorizes challenges (Web, Binary, Crypto, Forensics, etc.)
- 📝 **Professional Formatting**: Generates markdown with proper syntax highlighting
- 🛠️ **Tool Recognition**: Identifies and documents tools used during the solve
- 🎨 **Multiple Templates**: Academic, speedrun, tutorial, and portfolio styles
- 📤 **Export Options**: Markdown, PDF, HTML formats

## Installation

### Via ClawHub (Recommended)

```bash
# Install globally
npm install -g clawhub

# Install the skill
clawhub install ctf-writeup-generator
```

### Manual Installation

1. Clone or download this skill directory
2. Copy to your OpenClaw skills folder:
   ```bash
   cp -r ctf-writeup-generator ~/.openclaw/skills/
   ```
3. Restart OpenClaw or reload skills

## Usage

Simply ask your OpenClaw agent to generate a writeup:

```
"Generate a CTF writeup for the Binary Bash challenge I just solved"
"Create a writeup for this web exploitation challenge"
"Document my forensics challenge solution"
```

### Example Conversation

**You**: I just solved a buffer overflow challenge called "Stack Smasher" from HackTheBox. I used gdb and python to craft the exploit. The flag was HTB{st4ck_sm4sh1ng_fun}. Can you create a writeup?

**OpenClaw**: 
- Asks for additional details (exact steps, tools, payloads)
- Generates a professional writeup with:
  - Challenge metadata
  - Step-by-step solution
  - Code blocks with syntax highlighting
  - Tools documentation
  - Learning takeaways
- Saves to `hackthebox_stack-smasher_writeup.md`

## Configuration

Set environment variables for personalization:

```bash
# In your shell config (~/.bashrc, ~/.zshrc, etc.)
export CTF_AUTHOR="akm626"
export CTF_PLATFORM="HackTheBox"
export CTF_WRITEUP_STYLE="tutorial"
export CTF_AUTO_SCREENSHOTS=false
```

## Platform Support

Supports writeup generation for:
- HackTheBox (HTB)
- TryHackMe (THM)
- OffSec (OSCP, OSWP, etc.)
- PicoCTF
- CTFtime competitions
- Custom platforms (just specify the name)

## Flag Formats Supported

- Standard: `CTF{...}`, `FLAG{...}`, `flag{...}`
- HackTheBox: `HTB{...}`
- TryHackMe: `THM{...}`
- Shaastra: `SHAASTRA{...}`, `Shaastra{...}`
- picoCTF: `picoCTF{...}`
- Custom formats (configurable via regex)

## Challenge Categories

Automatically detects:
- Web Exploitation
- Binary Exploitation
- Reverse Engineering
- Cryptography
- Forensics (Digital, Memory, Network)
- OSINT
- PWN
- Miscellaneous

## Output Structure

Generated writeups include:
1. **Header**: Challenge name, author, date, category, difficulty
2. **Summary**: Brief overview
3. **Challenge Description**: Original prompt
4. **Reconnaissance**: Initial enumeration
5. **Solution**: Step-by-step walkthrough with code blocks
6. **Tools Used**: Documented toolchain
7. **Flag**: Properly formatted flag
8. **Key Takeaways**: Learning points
9. **References**: Additional resources

## Advanced Usage

### Multi-Challenge Writeups

```
"Generate a writeup covering all 3 crypto challenges from today's CTF"
```

### Different Formats

```
"Create a speedrun-style writeup for this challenge"
"Generate an academic writeup with detailed explanations"
"Make a portfolio writeup for my GitHub"
```

### Export to PDF

```
"Generate a writeup and export it to PDF"
```

## Tips for Best Results

1. **Provide detailed notes**: Include commands, outputs, and observations
2. **Mention dead-ends**: Document what didn't work and why
3. **Include context**: Platform, CTF name, time spent
4. **Reference tools**: Name specific tools and versions used
5. **Add insights**: Your unique methodology and thought process

## Security & Ethics

- ⚠️ Never include real credentials or API keys
- ⚠️ Respect competition rules (don't publish during active CTFs)
- ⚠️ Add spoiler warnings for recent challenges
- ⚠️ Verify flag sharing is allowed by the platform
- ⚠️ Sanitize paths that reveal sensitive system info

## Dependencies

**Required**: None (works out of the box)

**Optional** (for enhanced features):
- `pandoc`: PDF export
- `pygments`: Enhanced syntax highlighting

Install optional dependencies:
```bash
# Ubuntu/Debian
sudo apt install pandoc python3-pygments

# macOS
brew install pandoc
pip3 install pygments
```

## Contributing

Contributions welcome! Areas for improvement:
- New flag format patterns
- Platform-specific templates
- Enhanced categorization logic
- Export format options
- Integration with other tools

## Example Output

See [example_writeup.md](./example_writeup.md) for a full example of generated output.

## Troubleshooting

**Issue**: Skill not loading
- Check `~/.openclaw/skills/ctf-writeup-generator/SKILL.md` exists
- Restart OpenClaw
- Check logs for errors

**Issue**: Flag not detected
- Ensure flag format matches platform conventions
- Check for typos in flag
- Manually specify flag format if non-standard

**Issue**: Wrong category assigned
- Provide more context in your solving description
- Manually specify category if needed
- Update categorization keywords

## License

MIT License - Free to use and modify

## Author

Created by a cybersecurity enthusiast for the CTF community.

Maintained by: [Your GitHub username]

## Version History

- **1.0.0** (2026-02-08): Initial release
  - Basic writeup generation
  - Flag format detection
  - Multiple platform support
  - Markdown export

## Links

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub Registry](https://clawhub.ai)
- [Report Issues](https://github.com/yourusername/ctf-writeup-generator/issues)

## Acknowledgments

Built for the cybersecurity education and CTF community. Special thanks to:
- OpenClaw contributors
- CTF platform creators (HTB, THM, OffSec, etc.)
- The security research community

---

**Star this skill on ClawHub if you find it useful!** ⭐
