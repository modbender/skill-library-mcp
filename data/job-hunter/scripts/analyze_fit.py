#!/usr/bin/env python3
"""
Job Fit Analyzer — Scores job listings against a candidate profile.

Usage: analyze_fit.py --profile profile.json --jobs jobs.json [--threshold 60]

Input:
  - profile.json: Candidate profile with skills, experience, preferences
  - jobs.json: Array of job listings with title, description, requirements

Output: JSON with scored and ranked jobs, fit analysis, and recommendations.
"""

import json
import sys
import argparse
import re
from collections import Counter

def load_json(path):
    with open(path) as f:
        return json.load(f)

def normalize(text):
    """Lowercase and clean text for matching."""
    return re.sub(r'[^a-z0-9\s+#.]', ' ', text.lower())

def extract_keywords(text):
    """Extract meaningful keywords from text."""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'shall', 'can', 'need', 'dare',
        'ought', 'used', 'this', 'that', 'these', 'those', 'i', 'me', 'my',
        'we', 'our', 'you', 'your', 'he', 'she', 'it', 'they', 'them',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
        'about', 'above', 'after', 'again', 'also', 'as', 'because', 'before',
        'between', 'through', 'during', 'if', 'into', 'over', 'then', 'under',
        'while', 'able', 'experience', 'working', 'work', 'team', 'role',
        'looking', 'join', 'company', 'opportunity', 'position', 'based',
        'including', 'across', 'within', 'well', 'new', 'etc', 'strong'
    }
    words = normalize(text).split()
    return [w for w in words if w not in stop_words and len(w) > 2]

def compute_skill_match(profile_skills, job_text):
    """Score how many profile skills appear in the job text."""
    job_normalized = normalize(job_text)
    matches = []
    misses = []
    for skill in profile_skills:
        skill_lower = skill.lower()
        if skill_lower in job_normalized:
            matches.append(skill)
        else:
            # Try partial match for multi-word skills
            words = skill_lower.split()
            if len(words) > 1 and any(w in job_normalized for w in words if len(w) > 3):
                matches.append(skill)
            else:
                misses.append(skill)
    return matches, misses

def compute_seniority_match(profile_level, job_title, job_text):
    """Check if seniority level matches."""
    combined = normalize(job_title + ' ' + job_text)
    
    senior_signals = ['senior', 'sr.', 'lead', 'principal', 'head of', 'director', 'vp', 'manager']
    junior_signals = ['junior', 'jr.', 'entry', 'associate', 'intern', 'trainee', 'graduate']
    mid_signals = ['mid-level', 'mid level', 'specialist', 'analyst', 'coordinator']
    
    job_level = 'mid'
    if any(s in combined for s in senior_signals):
        job_level = 'senior'
    elif any(s in combined for s in junior_signals):
        job_level = 'junior'
    
    level_map = {'junior': 1, 'mid': 2, 'senior': 3}
    profile_num = level_map.get(profile_level.lower(), 2)
    job_num = level_map.get(job_level, 2)
    
    diff = abs(profile_num - job_num)
    if diff == 0:
        return 100, job_level, "Perfect level match"
    elif diff == 1:
        direction = "stretch" if job_num > profile_num else "might be below your level"
        return 60, job_level, f"Close match — {direction}"
    else:
        return 20, job_level, "Significant level mismatch"

def compute_location_match(profile_locations, profile_remote, job_text, job_title):
    """Score location compatibility."""
    combined = normalize(job_text + ' ' + job_title)
    
    if 'remote' in combined or 'work from home' in combined or 'wfh' in combined:
        if profile_remote:
            return 100, "Remote — perfect match"
        return 80, "Remote available"
    
    if 'hybrid' in combined:
        for loc in profile_locations:
            if loc.lower() in combined:
                return 90, f"Hybrid in {loc}"
        return 50, "Hybrid — check location"
    
    for loc in profile_locations:
        if loc.lower() in combined:
            return 100, f"On-site in {loc} — matches your location"
    
    return 30, "Location may not match — check listing"

def analyze_job(profile, job):
    """Full fit analysis for a single job."""
    title = job.get('title', '')
    description = job.get('description', '')
    combined_text = f"{title} {description}"
    
    # 1. Skill match (40% weight)
    all_skills = profile.get('skills', []) + profile.get('tools', [])
    matched_skills, missing_skills = compute_skill_match(all_skills, combined_text)
    skill_score = min(100, (len(matched_skills) / max(len(all_skills), 1)) * 150)  # Boost: don't need ALL skills
    
    # 2. Seniority match (25% weight)
    seniority_score, job_level, seniority_note = compute_seniority_match(
        profile.get('level', 'mid'), title, description
    )
    
    # 3. Location match (15% weight)
    location_score, location_note = compute_location_match(
        profile.get('locations', []),
        profile.get('open_to_remote', True),
        combined_text, title
    )
    
    # 4. Industry/domain match (10% weight)
    domain_keywords = profile.get('preferred_domains', [])
    domain_matches = [d for d in domain_keywords if d.lower() in normalize(combined_text)]
    domain_score = min(100, (len(domain_matches) / max(len(domain_keywords), 1)) * 200) if domain_keywords else 70
    
    # 5. Red flags (10% weight)
    red_flag_score = 100
    red_flags = []
    exclude = [x.lower() for x in profile.get('exclude_companies', [])]
    
    # Check excluded companies
    for company in exclude:
        if company in normalize(combined_text):
            red_flag_score = 0
            red_flags.append(f"Excluded company: {company}")
    
    # Check deal-breakers
    dealbreakers = [x.lower() for x in profile.get('dealbreakers', [])]
    for db in dealbreakers:
        if db in normalize(combined_text):
            red_flag_score = max(0, red_flag_score - 50)
            red_flags.append(f"Dealbreaker: {db}")
    
    # Weighted total
    total = (
        skill_score * 0.40 +
        seniority_score * 0.25 +
        location_score * 0.15 +
        domain_score * 0.10 +
        red_flag_score * 0.10
    )
    
    return {
        'job': job,
        'score': round(total),
        'breakdown': {
            'skills': {'score': round(skill_score), 'matched': matched_skills, 'missing': missing_skills[:5]},
            'seniority': {'score': seniority_score, 'detected_level': job_level, 'note': seniority_note},
            'location': {'score': location_score, 'note': location_note},
            'domain': {'score': round(domain_score), 'matched': domain_matches},
            'red_flags': {'score': red_flag_score, 'flags': red_flags}
        },
        'verdict': 'great_fit' if total >= 75 else 'good_fit' if total >= 55 else 'stretch' if total >= 40 else 'skip'
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze job fit against candidate profile')
    parser.add_argument('--profile', required=True, help='Path to candidate profile JSON')
    parser.add_argument('--jobs', required=True, help='Path to jobs JSON array')
    parser.add_argument('--threshold', type=int, default=0, help='Minimum score to include (0-100)')
    args = parser.parse_args()
    
    profile = load_json(args.profile)
    jobs = load_json(args.jobs)
    
    results = [analyze_job(profile, job) for job in jobs]
    results.sort(key=lambda x: x['score'], reverse=True)
    
    if args.threshold > 0:
        results = [r for r in results if r['score'] >= args.threshold]
    
    output = {
        'total_analyzed': len(jobs),
        'total_passing': len(results),
        'results': results,
        'summary': {
            'great_fit': len([r for r in results if r['verdict'] == 'great_fit']),
            'good_fit': len([r for r in results if r['verdict'] == 'good_fit']),
            'stretch': len([r for r in results if r['verdict'] == 'stretch']),
            'skip': len([r for r in results if r['verdict'] == 'skip'])
        }
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
