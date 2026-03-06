import re

def validate_titles(titles_list):
    """
    Filters a list of titles based on Xiaohongshu algorithm preferences.
    Returns: (valid_titles, rejected_titles)
    """
    
    # 1. Configuration
    MAX_LENGTH = 22  # Optimal visual length
    MIN_LENGTH = 8   # Too short is bad for SEO
    
    BANNED_WORDS = [
        "第一", "顶级", "最强", "治愈", "100%", "国家级", # Ad Law
        "综上所述", "此外", "探索", "不仅...而且"        # AI Fingerprints
    ]
    
    REQUIRED_CHARS = ["!", "?", "...", "✨", "🔥", "😭", "💰", "✅", "❌"]
    
    valid = []
    rejected = []

    # 2. Validation Loop
    for title in titles_list:
        reasons = []
        
        # Check Length
        if len(title) > MAX_LENGTH:
            reasons.append("Too Long (>22)")
        if len(title) < MIN_LENGTH:
            reasons.append("Too Short (<8)")
            
        # Check Banned Words
        for word in BANNED_WORDS:
            if word in title:
                reasons.append(f"Banned Word: {word}")
                break
                
        # Check Engagement (Emoji/Punctuation)
        has_visual_hook = any(char in title for char in REQUIRED_CHARS)
        if not has_visual_hook:
            reasons.append("No Visual Hook (Emoji/Punctuation)")
            
        # Decision
        if not reasons:
            valid.append(title)
        else:
            rejected.append({"title": title, "reasons": reasons})
            
    return valid, rejected

# Example of how the agent 'thinks' using this script:
# input_titles = ["Title A...", "Title B..."]
# final_list, _ = validate_titles(input_titles)
# return final_list