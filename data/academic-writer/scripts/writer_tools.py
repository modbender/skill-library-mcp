import os
import sys
import subprocess
import json
import glob
try:
    from docx import Document
except ImportError:
    Document = None

def read_reference(file_path):
    """读取参考资料"""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    try:
        if file_path.endswith('.docx'):
            if Document is None:
                return "Error: python-docx not installed. Run `pip install python-docx`."
            doc = Document(file_path)
            full_text = [para.text for para in doc.paragraphs]
            return '\n'.join(full_text)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def scan_template(directory="."):
    """扫描 LaTeX 结构"""
    tex_files = glob.glob(os.path.join(directory, "*.tex"))
    bib_files = glob.glob(os.path.join(directory, "*.bib"))
    
    main_file = None
    structure = {}
    
    for f_path in tex_files:
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # 简单启发式查找主文件
            if "\\documentclass" in content and "\\begin{document}" in content:
                main_file = os.path.basename(f_path)
            # 截取前 800 字符供 LLM 理解模板头部
            structure[os.path.basename(f_path)] = content[:800] + "\n...(truncated)"

    return json.dumps({
        "detected_main_file": main_file,
        "tex_files": [os.path.basename(f) for f in tex_files],
        "bib_files": [os.path.basename(f) for f in bib_files],
        "file_previews": structure
    }, ensure_ascii=False)

def write_latex_content(filename, content, mode='w'):
    """写入文件"""
    try:
        with open(filename, mode, encoding='utf-8') as f:
            f.write(content)
        return f"Success: Wrote {len(content)} chars to {filename}"
    except Exception as e:
        return f"Error writing: {str(e)}"

def compile_pdf(main_file):
    """编译 PDF"""
    if not main_file:
        return "Error: No main file specified."
    
    # 检查 latexmk 是否存在
    if subprocess.call(["which", "latexmk"], stdout=subprocess.DEVNULL) != 0:
        return "Error: latexmk not found. Please install texlive-full."

    try:
        # -interaction=nonstopmode: 不因错误暂停
        # -pdf: 生成 PDF
        result = subprocess.run(
            ['latexmk', '-pdf', '-interaction=nonstopmode', main_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60 # 防止死循环
        )
        
        if result.returncode == 0:
            return f"Success! PDF generated: {main_file.replace('.tex', '.pdf')}"
        else:
            # 提取最后部分的错误日志
            logs = result.stdout + "\n" + result.stderr
            return f"Compilation Failed. Error Log Tail:\n{logs[-1500:]}"
    except Exception as e:
        return f"Execution Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 writer_tools.py <command> [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "read_reference":
        print(read_reference(args[0] if args else ""))
    elif cmd == "scan_template":
        print(scan_template(args[0] if args else "."))
    elif cmd == "write_latex":
        # write_latex filename content mode
        filename = args[0]
        content = args[1]
        mode = args[2] if len(args) > 2 else 'w'
        print(write_latex_content(filename, content, mode))
    elif cmd == "compile_pdf":
        print(compile_pdf(args[0] if args else ""))
    else:
        print(f"Unknown command: {cmd}")