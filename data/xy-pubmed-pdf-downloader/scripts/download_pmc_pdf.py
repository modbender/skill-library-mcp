#!/usr/bin/env python3
"""
PMC/PubMed PDF Downloader
下载 PubMed Central (PMC) 开放获取论文的 PDF 文件

支持来源:
- PubMed Central (PMC)
- Europe PMC
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)


class PMCPDFDownloader:
    """PubMed Central PDF 下载器"""
    
    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
    
    def extract_pmc_id(self, identifier: str) -> str:
        """从各种格式提取 PMC ID"""
        identifier = identifier.strip()
        
        # 直接是 PMC ID (PMC12345678 或 12345678)
        if identifier.upper().startswith("PMC"):
            return identifier[3:]
        if identifier.isdigit() and len(identifier) >= 6:
            return identifier
        
        # 从 PMC URL 提取
        if "ncbi.nlm.nih.gov" in identifier:
            # PMC URL
            match = re.search(r"/articles/(?:PMC)?(\d+)", identifier)
            if match:
                return match.group(1)
            # PubMed URL (PMID)
            match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", identifier)
            if match:
                pmid = match.group(1)
                print(f"检测到 PubMed ID: {pmid}，正在转换为 PMC ID...")
                return self._pmid_to_pmcid(pmid)
        
        # 从 DOI 提取
        if identifier.startswith("10."):
            return self._doi_to_pmcid(identifier)
        
        raise ValueError(f"无法识别 identifier: {identifier}")
    
    def _pmid_to_pmcid(self, pmid: str) -> str:
        """通过 NCBI API 将 PMID 转换为 PMC ID"""
        url = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"
        params = {"ids": pmid, "format": "json", "idtype": "pmid"}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            data = response.json()
            
            if "records" in data and len(data["records"]) > 0:
                record = data["records"][0]
                if "pmcid" in record:
                    pmcid = record["pmcid"].replace("PMC", "")
                    print(f"转换成功: PMID {pmid} -> PMC{pmcid}")
                    return pmcid
                else:
                    raise ValueError(f"PMID {pmid} 没有对应的 PMC ID，可能不是开放获取文章")
        except Exception as e:
            if "不是开放获取" in str(e):
                raise
            print(f"PMID 转换失败: {e}")
        
        raise ValueError(f"无法将 PMID 转换为 PMC ID: {pmid}")
    
    def _doi_to_pmcid(self, doi: str) -> str:
        """通过 NCBI API 将 DOI 转换为 PMC ID"""
        url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        params = {"ids": doi, "format": "json", "idtype": "doi"}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            data = response.json()
            
            if "records" in data and len(data["records"]) > 0:
                record = data["records"][0]
                if "pmcid" in record:
                    return record["pmcid"].replace("PMC", "")
        except Exception as e:
            print(f"DOI 转换失败: {e}")
        
        raise ValueError(f"无法将 DOI 转换为 PMC ID: {doi}")
    
    def download_pdf(self, identifier: str, filename: str = None) -> Path:
        """下载指定 identifier 的 PDF"""
        pmc_id = self.extract_pmc_id(identifier)
        
        # 构造输出文件名
        if not filename:
            filename = f"PMC{pmc_id}.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        output_path = self.output_dir / filename
        
        print(f"正在处理: {identifier}")
        print(f"PMC ID: PMC{pmc_id}")
        print(f"保存到: {output_path}")
        
        # 尝试 Europe PMC (通常更可靠)
        europe_pmc_url = f"https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC{pmc_id}&blobtype=pdf"
        
        print(f"\n尝试 [Europe PMC]: {europe_pmc_url}")
        try:
            response = self.session.get(europe_pmc_url, timeout=120, stream=True)
            
            if response.status_code == 200:
                # 检查内容类型
                content_type = response.headers.get('Content-Type', '').lower()
                
                # 直接下载整个文件
                with open(output_path, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                
                # 验证文件
                if output_path.stat().st_size < 1000:
                    print(f"  文件太小 ({output_path.stat().st_size} bytes)，可能不是 PDF")
                    output_path.unlink()
                elif not self._is_pdf_file(output_path):
                    print(f"  文件不是有效的 PDF 格式")
                    output_path.unlink()
                else:
                    file_size_mb = output_path.stat().st_size / 1024 / 1024
                    print(f"✓ 下载成功")
                    print(f"  文件: {output_path}")
                    print(f"  大小: {file_size_mb:.2f} MB")
                    return output_path
        except Exception as e:
            print(f"  失败: {e}")
        
        raise Exception(f"无法下载 PMC{pmc_id}，可能不是开放获取文章")
    
    def _is_pdf_file(self, filepath: Path) -> bool:
        """检查文件是否是有效的 PDF"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except:
            return False
    
    def batch_download(self, identifiers: list, delay: float = 1.0):
        """批量下载多个 PDF"""
        results = []
        
        for i, identifier in enumerate(identifiers, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(identifiers)}] 处理: {identifier}")
            print('='*60)
            try:
                path = self.download_pdf(identifier)
                results.append({"identifier": identifier, "status": "success", "path": str(path)})
            except Exception as e:
                results.append({"identifier": identifier, "status": "failed", "error": str(e)})
            
            if i < len(identifiers):
                time.sleep(delay)
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="下载 PubMed Central (PMC) 开放获取论文的 PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s PMC12867338
  %(prog)s 12867338 -o ./papers
  %(prog)s 10.3389/fcvm.2024.1368022 -f my_paper.pdf
  %(prog)s --batch pmc_list.txt
        """
    )
    parser.add_argument(
        "identifier",
        nargs="?",
        help="PMC ID (如 PMC12345678 或 12345678)、PubMed URL 或 DOI"
    )
    parser.add_argument(
        "-o", "--output",
        default="./downloads",
        help="输出目录 (默认: ./downloads)"
    )
    parser.add_argument(
        "-f", "--filename",
        help="自定义文件名 (可选)"
    )
    parser.add_argument(
        "--batch",
        help="批量下载，从文件读取 ID 列表 (每行一个)"
    )
    
    args = parser.parse_args()
    
    if not args.identifier and not args.batch:
        parser.print_help()
        sys.exit(1)
    
    downloader = PMCPDFDownloader(output_dir=args.output)
    
    if args.batch:
        with open(args.batch, "r") as f:
            identifiers = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        print(f"批量下载 {len(identifiers)} 个文件...")
        results = downloader.batch_download(identifiers)
        
        success = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - success
        print(f"\n{'='*60}")
        print(f"下载完成: {success} 成功, {failed} 失败")
        print('='*60)
        
        if failed > 0:
            print("\n失败的条目:")
            for r in results:
                if r["status"] == "failed":
                    print(f"  - {r['identifier']}: {r.get('error', 'Unknown')}")
    else:
        try:
            downloader.download_pdf(args.identifier, args.filename)
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
