#!/usr/bin/env python3
"""
Fetch EdStem threads for any course and save with staff/student differentiation

Usage: 
    python3 fetch-edstem.py <course_id> [output_dir] [--course-name NAME]
    
Examples:
    python3 fetch-edstem.py 92041
    python3 fetch-edstem.py 92041 ./ml-course
    python3 fetch-edstem.py 92041 --course-name "Machine Learning"
    python3 fetch-edstem.py 92041 ./ml-course --course-name "Machine Learning"
"""

import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime

ED_TOKEN = "dptT0u.adkdSAKHoFQpttiLLmuxaJRqxekDmNMIxaYZgLUn"
ED_BASE = "https://us.edstem.org/api"

def fetch_course_info(course_id):
    """Get course info including staff list"""
    headers = {"Authorization": f"Bearer {ED_TOKEN}"}
    resp = requests.get(f"{ED_BASE}/user", headers=headers)
    resp.raise_for_status()
    user_data = resp.json()
    
    # Find the course
    for entry in user_data['courses']:
        if entry['course']['id'] == course_id:
            return entry['course']
    
    raise ValueError(f"Course {course_id} not found")

def fetch_threads(course_id, limit=50):
    """Fetch recent threads for a course"""
    headers = {"Authorization": f"Bearer {ED_TOKEN}"}
    resp = requests.get(
        f"{ED_BASE}/courses/{course_id}/threads",
        params={"limit": limit, "sort": "new"},
        headers=headers
    )
    resp.raise_for_status()
    return resp.json()['threads']

def fetch_thread_detail(thread_id):
    """Fetch full thread with comments"""
    headers = {"Authorization": f"Bearer {ED_TOKEN}"}
    resp = requests.get(f"{ED_BASE}/threads/{thread_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()['thread']

def is_staff(user_role):
    """Check if user is staff (instructor/TA)"""
    return user_role in ['staff', 'admin', 'tutor']

def format_thread_markdown(thread):
    """Format thread as markdown with staff differentiation"""
    md = []
    md.append(f"# Thread #{thread['number']}: {thread['title']}")
    md.append(f"**Category:** {thread['category']}")
    md.append(f"**Posted:** {thread['created_at']}")
    
    # Handle cases where user might not be present
    if 'user' in thread and thread['user']:
        author = thread['user']['name']
        role = '[STAFF]' if is_staff(thread['user'].get('role')) else '[STUDENT]'
        md.append(f"**Author:** {author} {role}")
    else:
        md.append(f"**Author:** (Unknown)")
    
    md.append("")
    md.append("---")
    md.append("")
    
    # Main post content (simplified - would need XML parsing for full content)
    md.append("## Original Post")
    md.append("")
    md.append(thread.get('document', '(Content unavailable)'))
    md.append("")
    
    # Answers
    if thread.get('answers'):
        md.append("## Answers")
        md.append("")
        for ans in thread['answers']:
            if 'user' in ans and ans['user']:
                author = ans['user']['name']
                role = '[STAFF]' if is_staff(ans['user'].get('role')) else '[STUDENT]'
            else:
                author = '(Unknown)'
                role = ''
            md.append(f"### {author} {role}")
            md.append(f"*Posted: {ans['created_at']}*")
            md.append("")
            md.append(ans.get('document', '(Content unavailable)'))
            md.append("")
    
    # Comments
    if thread.get('comments'):
        md.append("## Comments")
        md.append("")
        for comment in thread['comments']:
            if 'user' in comment and comment['user']:
                author = comment['user']['name']
                role = '[STAFF]' if is_staff(comment['user'].get('role')) else '[STUDENT]'
            else:
                author = '(Unknown)'
                role = ''
            md.append(f"- **{author} {role}:** {comment.get('content', '(Content unavailable)')}")
        md.append("")
    
    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(
        description='Fetch EdStem threads for any course',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 fetch-edstem.py 92041
  python3 fetch-edstem.py 92041 ./ml-course
  python3 fetch-edstem.py 92041 --course-name "Machine Learning"
  python3 fetch-edstem.py 92041 ./ml-course --course-name "Machine Learning"
        """
    )
    
    parser.add_argument('course_id', type=int, help='EdStem course ID')
    parser.add_argument('output_dir', nargs='?', default=None,
                       help='Output directory for threads (default: ./edstem-<course_id>)')
    parser.add_argument('--course-name', type=str, default=None,
                       help='Course name for display purposes')
    parser.add_argument('--limit', type=int, default=10,
                       help='Number of threads to fetch (default: 10)')
    
    args = parser.parse_args()
    
    course_id = args.course_id
    
    # Determine output directory
    if args.output_dir:
        edstem_dir = Path(args.output_dir)
    else:
        edstem_dir = Path(f"./edstem-{course_id}")
    
    edstem_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch course info if course name not provided
    course_name = args.course_name
    if not course_name:
        try:
            course_info = fetch_course_info(course_id)
            course_name = course_info.get('name', f'Course {course_id}')
        except Exception as e:
            print(f"Warning: Could not fetch course info: {e}")
            course_name = f"Course {course_id}"
    
    print(f"Fetching threads for {course_name} (ID: {course_id})...")
    
    # Fetch threads
    threads = fetch_threads(course_id, limit=max(args.limit, 50))
    
    # Save threads list
    with open(edstem_dir / "threads.json", "w") as f:
        json.dump(threads, f, indent=2)
    
    print(f"Found {len(threads)} threads. Fetching details for {args.limit} most recent...")
    
    # Fetch and save each thread
    for thread in threads[:args.limit]:
        thread_id = thread['id']
        thread_num = thread['number']
        
        print(f"  Thread #{thread_num}: {thread['title']}")
        
        detail = fetch_thread_detail(thread_id)
        md_content = format_thread_markdown(detail)
        
        with open(edstem_dir / f"thread-{thread_num:03d}.md", "w") as f:
            f.write(md_content)
    
    print(f"✅ Done! Threads saved to {edstem_dir.resolve()}/")

if __name__ == "__main__":
    main()
