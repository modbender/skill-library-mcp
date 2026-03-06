import os
import sys
import time
import argparse
import json
import requests
import pandas as pd
import re
from datetime import datetime, timedelta
from pdfminer.high_level import extract_text
import crawler  # Import the module to access globals
from crawler import run_crawl_task

def get_target_date():
    """
    Calculate the target start date for crawling based on the current weekday.
    Logic:
    - If today is Monday (weekday=0), start from last Friday (3 days ago).
    - Otherwise, start from yesterday (1 day ago).
    This logic matches the default behavior in the GUI version.
    """
    now = datetime.now()
    if now.weekday() == 0:  # Monday
        target_date = now - timedelta(days=3)
    else:
        target_date = now - timedelta(days=1)
    return target_date.strftime("%Y-%m-%d")

def log_callback(msg):
    """
    Simple logging callback that prints to stdout with a timestamp.
    CoPAW or other schedulers can capture this output.
    """
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")
    sys.stdout.flush()  # Ensure logs are flushed immediately

def extract_content_from_pdf(pdf_path):
    """
    Extract text from a PDF file using pdfminer.six.
    """
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        log_callback(f"Error extracting text from {pdf_path}: {e}")
        return ""

def call_llm_analysis(text, file_name, log_cb=log_callback):
    """
    Call LLM to extract structured data from the text.
    """
    # Define the columns as requested by the user
    columns = [
        '文件名', '标题', '交易基准日', '未偿本金总额', '资产笔数', '未偿利息总额', '借款人户数', '未偿本息总额', 
        '加权平均逾期天数', '其他费用', '单一借款人最高未偿本息余额', '借款人平均未偿本息余额', '借款人加权平均年龄', 
        '借款人加权平均授信额度', '五级分类情况', '核销情况', '担保情况概述', '诉讼情况概述', '备注', 
        '竞价报名截止时间', '竞价日', '转让方式', '竞价方式', '自由竞价开始时间', '自由竞价结束时间', 
        '延时周期（分钟）', '起始价（元）', '加价幅度（元）', '发布日期'
    ]
    
    prompt = f"""
    你是一个金融数据提取助手。请从以下不良贷款转让公告的文本中提取关键信息。
    请提取以下字段的值，并返回一个合法的 JSON 对象。
    
    需要提取的字段:
    {', '.join(columns)}
    
    注意:
    - '文件名' 字段请填写: '{file_name}'
    - 如果某个字段在文本中没有找到，请使用空字符串 ""。
    - 日期字段请统一格式为 YYYYMMDD 或 YYYY-MM-DD。
    - 金额字段请尽量保留数值，如果包含单位请保留单位。
    - 只返回 JSON 对象，不要包含 markdown 格式标记（如 ```json ... ```）。
    
    文本内容:
    {text[:15000]} 
    """
    
    # Get API configuration from environment variables
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("LLM_MODEL", "deepseek-chat")
    provider = os.getenv("LLM_PROVIDER", "deepseek").lower()

    # Provider specific default configurations
    if provider == "siliconflow" or provider == "硅基流动":
        # SiliconFlow default
        if not os.getenv("LLM_API_BASE"):
            api_base = "https://api.siliconflow.cn/v1"
        if not os.getenv("LLM_MODEL"):
            model_name = "deepseek-ai/DeepSeek-V3" # Common model on SiliconFlow
    elif provider == "qwen" or provider == "dashscope" or provider == "通义千问":
        # DashScope (Aliyun) default - usually requires compatible OpenAI client or specific URL
        # Here we assume using OpenAI-compatible endpoint if available, or user sets BASE_URL
        if not os.getenv("LLM_API_BASE"):
            api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        if not os.getenv("LLM_MODEL"):
            model_name = "qwen-plus"
    
    if not api_key:
        log_cb("Skipping LLM analysis: LLM_API_KEY environment variable not set.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that extracts data into JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(f"{api_base}/chat/completions", headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Clean up potential markdown code blocks
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        return json.loads(content)
    except Exception as e:
        log_cb(f"LLM Call failed for {file_name}: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            log_cb(f"Response text: {response.text}")
        return None

def process_downloaded_files(pdf_dir, excel_path, log_cb=log_callback):
    """
    Iterate through downloaded files and perform LLM analysis.
    """
    log_cb(f"Starting analysis for files in directory: {pdf_dir}")
    
    if not os.path.exists(pdf_dir):
        log_cb(f"Directory not found: {pdf_dir}")
        return

    # Path for the analysis result Excel
    analysis_excel_path = os.path.join(pdf_dir, "analysis_result.xlsx")
    
    # Load existing analysis to avoid re-processing
    processed_files = set()
    df_existing = pd.DataFrame()
    
    if os.path.exists(analysis_excel_path):
        try:
            df_existing = pd.read_excel(analysis_excel_path)
            if '文件名' in df_existing.columns:
                processed_files = set(df_existing['文件名'].astype(str))
            log_cb(f"Loaded existing analysis records: {len(df_existing)}")
        except Exception as e:
            log_cb(f"Error loading existing analysis file: {e}")
            df_existing = pd.DataFrame()
    
    # Load the crawl log to find files
    if not os.path.exists(excel_path):
        log_cb(f"Crawl log not found: {excel_path}")
        return
        
    try:
        wb = pd.read_excel(excel_path)
    except Exception as e:
        log_cb(f"Failed to read crawl log: {e}")
        return

    new_results = []
    
    # Check for API Key presence
    if not os.getenv("LLM_API_KEY"):
        log_cb("Warning: LLM_API_KEY is not set. Only text extraction will be attempted (but not saved). Please set LLM_API_KEY to enable analysis.")
        return

    for index, row in wb.iterrows():
        pdf_name = str(row.get('PDF文件名', ''))
        pdf_path = str(row.get('保存路径', ''))
        
        if not pdf_name or not pdf_path or pdf_path == "nan" or pdf_name == "nan":
            continue
            
        if pdf_name in processed_files:
            continue
            
        # Handle relative paths or verify existence
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.join(pdf_dir, pdf_path)
            
        if not os.path.exists(pdf_path):
            # Try to find it in the directory by name
            potential_path = os.path.join(pdf_dir, pdf_name)
            if os.path.exists(potential_path):
                pdf_path = potential_path
            else:
                # log_cb(f"File not found: {pdf_path}")
                continue
        
        # Skip non-PDF files (e.g. .txt) for now unless logic supports it
        if not pdf_path.lower().endswith('.pdf'):
            continue
            
        log_cb(f"Analyzing new file: {pdf_name}")
        
        # Extract text
        text = extract_content_from_pdf(pdf_path)
        if not text or len(text.strip()) < 10:
            log_cb(f"Text extraction failed or empty for {pdf_name}")
            continue
            
        # Call LLM
        data = call_llm_analysis(text, pdf_name, log_cb)
        
        if data:
            # Ensure critical fields are present
            data['文件名'] = pdf_name
            if not data.get('发布日期'):
                data['发布日期'] = row.get('发布日期', '')
            if not data.get('标题'):
                data['标题'] = row.get('标题', '')
                
            new_results.append(data)
            log_cb(f"Analysis successful for {pdf_name}")
            
            # Save incrementally (optional, but safer)
            # For now, we collect and save at the end of batch
        
    if new_results:
        df_new = pd.DataFrame(new_results)
        
        # Ensure all target columns exist
        target_columns = [
            '文件名', '标题', '交易基准日', '未偿本金总额', '资产笔数', '未偿利息总额', '借款人户数', '未偿本息总额', 
            '加权平均逾期天数', '其他费用', '单一借款人最高未偿本息余额', '借款人平均未偿本息余额', '借款人加权平均年龄', 
            '借款人加权平均授信额度', '五级分类情况', '核销情况', '担保情况概述', '诉讼情况概述', '备注', 
            '竞价报名截止时间', '竞价日', '转让方式', '竞价方式', '自由竞价开始时间', '自由竞价结束时间', 
            '延时周期（分钟）', '起始价（元）', '加价幅度（元）', '发布日期'
        ]
        
        # Add missing columns with empty strings
        for col in target_columns:
            if col not in df_new.columns:
                df_new[col] = ""
                
        # Reorder columns
        df_new = df_new[target_columns]
        
        # Combine with existing
        if not df_existing.empty:
            # Ensure existing df has same columns
            for col in target_columns:
                if col not in df_existing.columns:
                    df_existing[col] = ""
            df_final = pd.concat([df_existing[target_columns], df_new], ignore_index=True)
        else:
            df_final = df_new
            
        try:
            df_final.to_excel(analysis_excel_path, index=False)
            log_cb(f"Successfully saved analysis results to {analysis_excel_path}")
        except Exception as e:
            log_cb(f"Error saving Excel: {e}")
    else:
        log_cb("No new files to analyze or analysis failed.")

def main():
    parser = argparse.ArgumentParser(description="Run scheduled crawl for Yindeng announcements and optionally analyze with LLM.")
    parser.add_argument("date", nargs="?", help="Start date in YYYY-MM-DD format (e.g. 2025-01-01). Defaults to auto-calculation.")
    parser.add_argument("--analyze", action="store_true", help="Enable LLM analysis of downloaded documents.")
    parser.add_argument("--source", choices=["result", "announcement", "all"], default="all", help="Source to crawl: result (default), announcement, or all.")
    args = parser.parse_args()

    log_callback("Starting scheduled crawl task...")
    
    try:
        # 1. Determine the date range
        if args.date:
            try:
                datetime.strptime(args.date, "%Y-%m-%d")
                start_date_str = args.date
                log_callback(f"Using provided start date: {start_date_str}")
            except ValueError:
                log_callback(f"Invalid date format: {args.date}. Please use YYYY-MM-DD.")
                sys.exit(1)
        else:
            start_date_str = get_target_date()
            log_callback(f"Auto-calculated target start date: {start_date_str}")
        
        # Determine tasks
        tasks = []
        if args.source == "all":
            tasks = ["announcement", "result"]
        else:
            tasks = [args.source]
            
        total_added = 0
        all_no_update = True
        
        for task_name in tasks:
            log_callback(f"=== Starting task: {task_name} ===")
            pdf_dir, excel_path, added, no_update = run_crawl_task(task_name, start_date_str=start_date_str, log_cb=log_callback)
            
            total_added += (added or 0)
            if not no_update:
                all_no_update = False
                
            log_callback(f"Task {task_name} completed, added rows: {added}")
            
            # 3. Run Analysis if requested (Only for 'result' or if generic analysis is desired)
            # Currently analysis logic is generic for downloaded PDFs, so we can run it for both if needed.
            if args.analyze and pdf_dir and excel_path:
                log_callback(f"Starting LLM analysis phase for {task_name}...")
                process_downloaded_files(pdf_dir, excel_path, log_callback)
            elif args.analyze:
                log_callback(f"Skipping analysis for {task_name} due to missing output paths.")
        
        # Check for no updates (exit code 2 logic)
        # If ALL tasks had no updates, we exit with 2.
        if all_no_update:
            log_callback(f"{start_date_str}暂无更新 (All tasks)")
            sys.exit(2)
        
        log_callback(f"Scheduled task completed successfully. Total added rows: {total_added}")
        sys.exit(0)
        
    except SystemExit as se:
        raise se
    except Exception as e:
        log_callback(f"Error during scheduled crawl: {str(e)}")
        # Print full traceback for debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
