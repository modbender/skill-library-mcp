import os
import argparse
import re
import datetime

def load_blocks(shared_blocks_path):
    """Parses shared-blocks.md into a dictionary {block_name: block_content}."""
    blocks = {}
    if not os.path.exists(shared_blocks_path):
        print(f"Warning: Shared blocks file not found at {shared_blocks_path}")
        return blocks

    with open(shared_blocks_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by "## Block: "
    parts = re.split(r'^## Block: ', content, flags=re.MULTILINE)
    
    for part in parts[1:]:  # Skip preamble
        # First line is block name
        lines = part.split('\n')
        block_name = lines[0].strip()
        
        # Content is the rest, but we need to strip the markdown code block fences if present
        # The templates usually expect the content *inside* the fences? 
        # Actually looking at breadth.md:
        # {{INSERT: shared-blocks.md > Block: provided-sources}}
        # And provided-sources in shared-blocks.md has ``` ... ```. 
        # So we should include the fences if they are part of the block content in shared-blocks.md.
        # shared-blocks.md has the content wrapped in ```...```.
        # So we just take everything after the block name line.
        
        block_content = '\n'.join(lines[1:]).strip()
        blocks[block_name] = block_content

    return blocks

def process_template(template_path, blocks, substitutions):
    """Reads template, injects blocks, substitutes placeholders."""
    if not os.path.exists(template_path):
        print(f"Error: Template not found at {template_path}")
        return None

    with open(template_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Inject Blocks
    # Pattern: {{INSERT: shared-blocks.md > Block: block_name}}
    def replace_block(match):
        block_name = match.group(1).strip()
        if block_name in blocks:
            return blocks[block_name]
        else:
            print(f"Warning: Block '{block_name}' not found.")
            return f"[MISSING BLOCK: {block_name}]"

    text = re.sub(r'\{\{INSERT: shared-blocks\.md > Block: (.+?)\}\}', replace_block, text)

    # 2. Substitute Placeholders
    for key, value in substitutions.items():
        placeholder = f"{{{{{key}}}}}"
        text = text.replace(placeholder, str(value))

    # 3. Handle Inject Context (if not in substitutions, replace with empty)
    if "{{INJECT_CONTEXT}}" in text and "INJECT_CONTEXT" not in substitutions:
        text = text.replace("{{INJECT_CONTEXT}}", "")

    return text

def main():
    parser = argparse.ArgumentParser(description="Assemble research sub-agent prompts.")
    parser.add_argument("--topic", required=True, help="Research topic")
    parser.add_argument("--angle", required=True, help="Research angle/context")
    parser.add_argument("--workspace", required=True, help="Workspace path for this run")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="Date (YYYY-MM-DD)")
    parser.add_argument("--extracts", default="false", help="Save source extracts (true/false)")
    parser.add_argument("--skills-dir", default=".", help="Path to skills/researching-in-parallel directory")
    parser.add_argument("--context", default="", help="Additional context to inject")
    parser.add_argument("--mode", default="new", choices=["new", "update"], help="new or update report")
    parser.add_argument("--report-path", help="Path to existing report (for update mode)")

    args = parser.parse_args()

    # Setup paths
    refs_dir = os.path.join(args.skills_dir, "references", "prompts")
    shared_blocks_path = os.path.join(refs_dir, "shared-blocks.md")
    
    # Load blocks
    blocks = load_blocks(shared_blocks_path)

    # Slugify topic
    topic_slug = re.sub(r'[^a-z0-9]+', '-', args.topic.lower()).strip('-')

    # Substitutions
    subs = {
        "TOPIC": args.topic,
        "ANGLE": args.angle,
        "DATE": args.date,
        "WORKSPACE_PATH": args.workspace,
        "TOPIC_SLUG": topic_slug,
        "SAVE_SOURCE_EXTRACTS": args.extracts,
        "INJECT_CONTEXT": args.context
    }
    
    if args.report_path:
        subs["REPORT_TO_EDIT_PATH"] = args.report_path

    # Roles to process
    roles = ["breadth", "critical", "evidence"]
    if args.mode == "update":
        roles.append("updater")
    else:
        roles.append("synthesis") # Assuming 'review-report' is synthesis based on SKILL.md table

    # Process each role
    for role in roles:
        # Map role to filename
        if role == "synthesis":
            filename = "synthesis.md" 
        elif role == "updater":
            filename = "updater.md"
        else:
            filename = f"{role}.md"
            
        template_path = os.path.join(refs_dir, filename)
        
        # 'synthesis.md' might be named differently in refs/prompts? 
        # SKILL.md says: "Open the appropriate role prompt_template files... review-report (Synthesis) -> subagents.synthesis"
        # Let's check the file list again or just try 'synthesis.md' based on the file list I saw earlier.
        # Listing showed: breadth.md, critical.md, evidence.md, shared-blocks.md, synthesis.md, updater.md.
        # So 'synthesis.md' is correct.

        final_prompt = process_template(template_path, blocks, subs)
        
        if final_prompt:
            output_filename = f"prompt-{role}.md"
            output_path = os.path.join(args.workspace, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_prompt)
            print(f"Generated: {output_path}")

if __name__ == "__main__":
    main()
