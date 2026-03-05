# Vibe Coding Tools by Use Case

## Quick Decision Matrix

| You are... | Best tool |
|------------|-----------|
| Experienced dev wanting control | Cursor, Claude Code |
| Building quick prototypes | Bolt.new, Lovable |
| Working on large existing codebase | Windsurf, Cursor |
| Non-technical creator | Lovable, Replit |
| Learning to code | Replit, Bolt.new |
| Terminal-native dev | Claude Code |

## AI-Native IDEs (For Developers)

### Cursor
- **Strength**: Multi-file edits, full codebase awareness
- **Best for**: Existing projects, team codebases
- **Key feature**: `.cursorrules` for project context
- **Pricing**: Free to $200/mo

### Claude Code
- **Strength**: Terminal-based, raw power, highest benchmark scores
- **Best for**: Devs who live in terminal
- **Key feature**: Agentic multi-step execution
- **Pricing**: $20-$200/mo usage-based

### Windsurf
- **Strength**: Autonomous agent (Cascade), context management
- **Best for**: Large codebases, complex refactors
- **Pricing**: $15/mo Pro

## Browser-Based Builders (No Setup)

### Lovable
- **Strength**: Design-first, polished UI output
- **Best for**: MVPs with good UX requirements
- **Key feature**: Supabase integration built-in
- **Pricing**: From $25/mo

### Bolt.new
- **Strength**: Prompt to live URL fast
- **Best for**: Quick prototypes, demos
- **Key feature**: Generous free tier
- **Pricing**: Free tier, Pro ~$20/mo

### Replit
- **Strength**: Full browser IDE, instant deploy
- **Best for**: Learning, collaboration, instant sharing
- **Stat**: 75% of users never write code directly
- **Pricing**: Free tier, paid for more compute

## When to Use What

### Starting from Zero (no code yet)
1. **Just exploring**: Bolt.new (free, fast)
2. **Need good design**: Lovable (polished output)
3. **Want to learn**: Replit (educational mode)

### Adding to Existing Project
1. **Know the codebase well**: Cursor
2. **Codebase is complex**: Windsurf (better context handling)
3. **Terminal workflow**: Claude Code

### Team Collaboration
1. **Shared rules needed**: Cursor (rules files in repo)
2. **Quick demos**: Bolt.new or Lovable (shareable URLs)
3. **Pair programming**: Cursor with shared rules

## Tool-Specific Tips

### Cursor
- Use Composer for multi-file changes
- Keep .cursorrules updated with learnings
- `Cmd+K` for quick inline edits

### Claude Code
- Let it run — it's designed for autonomy
- Provide good CLAUDE.md for context
- Works well with existing terminal workflows

### Bolt.new
- Start minimal, iterate in small prompts
- Export code when you need more control
- Good for throwaway experiments

### Lovable
- Let it handle Supabase setup
- Focus prompts on user experience
- Better for consumer-facing apps

## Combining Tools

Common pattern:
1. **Prototype** in Bolt.new/Lovable (fast iteration)
2. **Export** when direction is clear
3. **Continue** in Cursor (more control for refinement)
4. **Deploy** with your normal infrastructure
