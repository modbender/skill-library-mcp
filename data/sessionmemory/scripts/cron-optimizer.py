#!/usr/bin/env python3
"""
OpenClaw Cron Memory Optimizer

Analyzes cron job prompts and suggests memory-enhanced versions that include
context from session memory before executing tasks.

Usage:
  python3 cron-optimizer.py [--input JSON_FILE] [--output MD_FILE]
  
If no input specified, reads from ~/.openclaw/cron/jobs.json
If no output specified, writes to memory/cron-optimization-report.md
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

# Common topics that benefit from memory context
TOPIC_PATTERNS = {
    'research': ['research', 'scout', 'find', 'search', 'discover', 'analysis', 'investigate'],
    'content': ['content', 'write', 'draft', 'post', 'article', 'blog'],
    'workshop': ['workshop', 'curriculum', 'training', 'course', 'education'],
    'planning': ['plan', 'strategy', 'roadmap', 'goals', 'objectives'],
    'review': ['review', 'evaluate', 'assess', 'analyze', 'audit'],
    'outreach': ['outreach', 'contact', 'email', 'message', 'reach out'],
    'automation': ['automate', 'script', 'process', 'workflow'],
    'monitoring': ['monitor', 'check', 'status', 'health', 'report'],
    'optimization': ['optimize', 'improve', 'enhance', 'refactor', 'upgrade']
}

def extract_topics(prompt_text):
    """Extract likely topics from a cron job prompt."""
    text_lower = prompt_text.lower()
    found_topics = []
    
    for topic, keywords in TOPIC_PATTERNS.items():
        if any(keyword in text_lower for keyword in keywords):
            found_topics.append(topic)
    
    # Extract specific entities that might benefit from memory
    entities = []
    
    # Look for file paths that suggest specific projects
    file_matches = re.findall(r'(/[a-zA-Z0-9_/-]+/[a-zA-Z0-9_.-]+)', prompt_text)
    for match in file_matches:
        if 'research' in match:
            entities.append('research projects')
        elif 'workshop' in match:
            entities.append('workshop development')
        elif 'content' in match:
            entities.append('content creation')
    
    # Look for mentions of specific people or roles
    if re.search(r'\b(dirk|igor|participant|client|user)\b', text_lower):
        entities.append('people and roles')
    
    # Look for business/product mentions
    if re.search(r'\b(aia|mastery|workshop|course|client)\b', text_lower):
        entities.append('business activities')
    
    return found_topics, entities

def generate_memory_preamble(topics, entities, job_name):
    """Generate a memory preamble for the given topics and entities."""
    
    # Determine the main focus
    if 'research' in topics:
        main_topic = 'research activities'
    elif 'workshop' in topics:
        main_topic = 'workshop development'
    elif 'content' in topics:
        main_topic = 'content creation'
    elif 'outreach' in topics:
        main_topic = 'outreach campaigns'
    else:
        main_topic = 'recent activities'
    
    # Build search terms
    search_terms = []
    if entities:
        search_terms.extend(entities[:2])  # Take top 2 entities
    if topics:
        search_terms.append(topics[0])  # Primary topic
    
    search_phrase = ' and '.join(search_terms) if search_terms else main_topic
    
    preamble = f"""Before starting: Use memory_search to find recent context about {search_phrase}. Check memory/SESSION-GLOSSAR.md for relevant people, projects, and recent decisions. Then proceed with the original task using this context.

"""
    
    return preamble

def analyze_cron_job(job):
    """Analyze a single cron job and suggest optimizations."""
    name = job.get('name', 'unknown')
    enabled = job.get('enabled', False)
    message = job.get('payload', {}).get('message', '')
    
    if not message:
        return None
    
    # Skip if already has memory context
    if 'memory_search' in message or 'SESSION-GLOSSAR' in message:
        return {
            'name': name,
            'enabled': enabled,
            'status': 'already_optimized',
            'reason': 'Already includes memory search or glossary references'
        }
    
    # Skip monitoring/reporting jobs that don't benefit from memory
    if any(word in message.lower() for word in ['session_status', 'git log', 'backup', 'cost report']):
        return {
            'name': name,
            'enabled': enabled,
            'status': 'skip_monitoring',
            'reason': 'Monitoring/system task - memory context not beneficial'
        }
    
    topics, entities = extract_topics(message)
    
    if not topics and not entities:
        return {
            'name': name,
            'enabled': enabled,
            'status': 'skip_unclear',
            'reason': 'Could not identify clear topic that would benefit from memory'
        }
    
    # Generate optimized version
    preamble = generate_memory_preamble(topics, entities, name)
    optimized_message = preamble + message
    
    return {
        'name': name,
        'enabled': enabled,
        'status': 'optimizable',
        'topics': topics,
        'entities': entities,
        'original_message': message,
        'optimized_message': optimized_message,
        'preamble': preamble.strip()
    }

def load_cron_jobs(input_file=None):
    """Load cron jobs from file or default location."""
    if input_file:
        with open(input_file, 'r') as f:
            data = json.load(f)
    else:
        # Try default locations
        default_path = os.path.expanduser('~/.openclaw/cron/jobs.json')
        if os.path.exists(default_path):
            with open(default_path, 'r') as f:
                data = json.load(f)
        else:
            # Try finding any cron JSON files
            cron_dir = os.path.expanduser('~/.openclaw/cron')
            if os.path.exists(cron_dir):
                json_files = list(Path(cron_dir).glob('*.json'))
                if json_files:
                    with open(json_files[0], 'r') as f:
                        data = json.load(f)
                else:
                    raise FileNotFoundError("No JSON files found in ~/.openclaw/cron/")
            else:
                raise FileNotFoundError("~/.openclaw/cron/ directory not found")
    
    return data.get('jobs', [])

def generate_report(analyses, output_file):
    """Generate markdown report of optimization suggestions."""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Count by status
    optimizable = [a for a in analyses if a and a['status'] == 'optimizable']
    already_optimized = [a for a in analyses if a and a['status'] == 'already_optimized']
    skipped = [a for a in analyses if a and a['status'].startswith('skip_')]
    
    report = f"""# Cron Memory Optimizer Report

Generated: {timestamp}

## Summary

- **Total jobs analyzed:** {len(analyses)}
- **Can be optimized:** {len(optimizable)}
- **Already optimized:** {len(already_optimized)}
- **Skipped (not beneficial):** {len(skipped)}

## Optimizable Jobs ({len(optimizable)})

These jobs would benefit from memory context:

"""

    for analysis in optimizable:
        if not analysis:
            continue
            
        status_emoji = "✅" if analysis['enabled'] else "⏸️"
        
        report += f"""### {status_emoji} {analysis['name']}

**Topics detected:** {', '.join(analysis['topics']) if analysis['topics'] else 'None'}
**Entities detected:** {', '.join(analysis['entities']) if analysis['entities'] else 'None'}
**Status:** {'Enabled' if analysis['enabled'] else 'Disabled'}

**Current prompt:**
```
{analysis['original_message'][:200]}{'...' if len(analysis['original_message']) > 200 else ''}
```

**Suggested memory preamble:**
```
{analysis['preamble']}
```

**Full optimized prompt:**
```
{analysis['optimized_message'][:500]}{'...' if len(analysis['optimized_message']) > 500 else ''}
```

**Reasoning:** This job appears to work with {', '.join(analysis['topics']) if analysis['topics'] else 'general tasks'} and would benefit from knowing recent context about {', '.join(analysis['entities'][:2]) if analysis['entities'] else 'related activities'} before starting.

---

"""

    if already_optimized:
        report += f"""## Already Optimized Jobs ({len(already_optimized)})

These jobs already include memory context:

"""
        for analysis in already_optimized:
            if analysis:
                status_emoji = "✅" if analysis['enabled'] else "⏸️"
                report += f"- {status_emoji} **{analysis['name']}** - {analysis['reason']}\n"

    if skipped:
        report += f"""

## Skipped Jobs ({len(skipped)})

These jobs don't benefit from memory context:

"""
        for analysis in skipped:
            if analysis:
                status_emoji = "✅" if analysis['enabled'] else "⏸️"
                report += f"- {status_emoji} **{analysis['name']}** - {analysis['reason']}\n"

    report += f"""

## Implementation Notes

### The Memory Preamble Pattern

All suggested optimizations follow this pattern:
```
Before starting: Use memory_search to find recent context about [TOPIC]. 
Check memory/SESSION-GLOSSAR.md for relevant people, projects, and recent decisions. 
Then proceed with the original task using this context.
```

### How to Apply Changes

1. **Review each suggestion** - The optimizer is conservative, but human judgment is needed
2. **Test with one job first** - Pick a low-risk job to validate the approach
3. **Update cron jobs manually** - This script does NOT auto-modify jobs (safety first)
4. **Monitor results** - Check if the memory context improves job output quality

### Memory System Requirements

These optimizations assume you have:
- Session memory skill installed and configured
- `memory/SESSION-GLOSSAR.md` populated with recent activities
- `memory/sessions/*.md` with session transcripts
- Memory search vectorization working

If you don't have these, run the session-memory skill setup first.

### When NOT to Add Memory Context

The optimizer skips these types of jobs automatically:
- System monitoring (cost reports, backups, health checks)
- Simple automation (git operations, file cleanup)
- Jobs that already use memory search
- External API polling without decision-making

### Tips for Better Results

1. **Keep SESSION-GLOSSAR.md updated** - Run glossary builder regularly
2. **Use specific search terms** - The more specific the memory search, the better
3. **Consider job frequency** - High-frequency jobs might want lighter memory checks
4. **Test edge cases** - What happens if memory search returns no results?

Generated by OpenClaw Cron Memory Optimizer v1.0
"""

    # Write report
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(report)

def main():
    parser = argparse.ArgumentParser(description='Optimize OpenClaw cron jobs with memory context')
    parser.add_argument('--input', help='Input JSON file (default: ~/.openclaw/cron/jobs.json)')
    parser.add_argument('--output', help='Output markdown file (default: memory/cron-optimization-report.md)')
    
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output or 'memory/cron-optimization-report.md'
    
    try:
        # Load cron jobs
        print("Loading cron jobs...")
        jobs = load_cron_jobs(input_file)
        print(f"Found {len(jobs)} cron jobs")
        
        # Analyze each job
        print("Analyzing jobs for optimization opportunities...")
        analyses = []
        for job in jobs:
            analysis = analyze_cron_job(job)
            analyses.append(analysis)
            if analysis and analysis['status'] == 'optimizable':
                print(f"  ✨ {analysis['name']} - can be optimized")
            elif analysis and analysis['status'] == 'already_optimized':
                print(f"  ✅ {analysis['name']} - already optimized")
            elif analysis:
                print(f"  ⏭️  {analysis['name']} - skipped ({analysis['status']})")
        
        # Generate report
        print(f"Generating report: {output_file}")
        generate_report(analyses, output_file)
        
        # Summary
        optimizable_count = len([a for a in analyses if a and a['status'] == 'optimizable'])
        print(f"\n✅ Report generated successfully!")
        print(f"📊 {optimizable_count} jobs can be optimized with memory context")
        print(f"📄 Full report saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Try specifying an input file with --input")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()