import os
import json

def analyze_docs_batch(file_paths):
    results = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract topic from filename
            filename = os.path.basename(file_path)
            # Remove hash and .txt extension, replace underscores with spaces
            topic = filename.split('_', 1)[1].replace('.txt', '').replace('_', ' ').strip()
            # Further clean up common suffixes like 'htm'
            topic = topic.replace('htm', '').strip()
            topic = topic.replace('Admin HV HTML page', '').strip()
            topic = topic.replace('Install HV HTML page', '').strip()
            topic = topic.replace('Scale Bench Guide HTML page', '').strip()
            topic = topic.replace('Scale Bench Guide HTML 97 page', '').strip()
            topic = topic.replace('z kb articles zertokbs page', '').strip()


            # Simple summarization and categorization (can be refined with LLM if needed for deeper analysis)
            summary = content[:500].strip() + "..." if len(content) > 500 else content.strip()

            category = "General/Overview" # Default
            if "install" in topic.lower() or "installation" in topic.lower() or "deploy" in topic.lower() or "setup" in topic.lower():
                category = "Installation/Setup"
            elif "configure" in topic.lower() or "setting" in topic.lower() or "pair" in topic.lower() or "routing" in topic.lower():
                category = "Configuration"
            elif "monitor" in topic.lower() or "performance" in topic.lower() or "report" in topic.lower():
                category = "Monitoring/Reporting"
            elif "troubleshoot" in topic.lower() or "error" in topic.lower() or "log" in topic.lower() or "diagnostic" in topic.lower():
                category = "Troubleshooting"
            elif "recovery" in topic.lower() or "failover" in topic.lower() or "restore" in topic.lower() or "migration" in topic.lower() or "clone" in topic.lower() or "move" in topic.lower():
                category = "Recovery/Migration"
            elif "vpg" in topic.lower() or "protection" in topic.lower() or "vm" in topic.lower() or "journal" in topic.lower() or "replication" in topic.lower() or "usage" in topic.lower():
                category = "Usage/Protection"
            elif "prereq" in topic.lower() or "requirement" in topic.lower() or "consideration" in topic.lower():
                category = "Prerequisites/Planning"
            elif "ltr" in topic.lower() or "advanced" in topic.lower() or "policy" in topic.lower():
                category = "Advanced Features"
            
            results.append({
                'file_path': file_path,
                'topic': topic,
                'summary': summary,
                'category': category
            })
        except Exception as e:
            results.append({
                'file_path': file_path,
                'error': str(e)
            })
    print(json.dumps(results)) # Print to stdout for OpenClaw to capture

if __name__ == "__main__":
    import sys
    # Expecting: python analyze_docs_batch.py <file_path_1> <file_path_2> ...
    file_paths = sys.argv[1:]
    analyze_docs_batch(file_paths)