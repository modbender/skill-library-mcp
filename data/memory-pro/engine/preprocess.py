from nltk.tokenize import sent_tokenize
import re
import os

def clean_text(text):
    """
    清理文本：移除代碼塊、Markdown 鏈接、標題等
    """
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'#+\s*.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_directory():
    default_workspace = os.path.expanduser("~/.openclaw/workspace/")
    default_memory = os.path.join(default_workspace, "memory")
    
    workspace_root = os.getenv("MEMORY_PRO_WORKSPACE_DIR", default_workspace)
    data_dir = os.getenv("MEMORY_PRO_DATA_DIR", default_memory)
    
    if not os.path.isabs(data_dir):
        data_dir = os.path.join(workspace_root, data_dir)
        
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")
    
    sentences = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned = clean_text(content)
            sentences.extend(sent_tokenize(cleaned))
    
    core_files_env = os.getenv("MEMORY_PRO_CORE_FILES", "MEMORY.md,SOUL.md,STATUS.md,AGENTS.md,USER.md")
    core_files = [f.strip() for f in core_files_env.split(',') if f.strip()]
    
    for filename in core_files:
        filepath = os.path.join(workspace_root, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned = clean_text(content)
            sentences.extend(sent_tokenize(cleaned))
    
    valid_sentences = [s for s in sentences if s.strip() and len(s.split()) > 3]
    return sorted(list(set(valid_sentences)))
