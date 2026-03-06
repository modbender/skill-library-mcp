import requests
from bs4 import BeautifulSoup
from typing import Dict, Any


def translate_key(key: str) -> str:
    """Translate key from Indonesian to English using a predefined dictionary."""
    translations = {
        "Nama": "name",
        "Kode": "code",
        "Alamat Kantor": "office_address",
        "Alamat Email": "email",
        "Telepon": "phone",
        "Fax": "fax",
        "NPWP": "tax_id",
        "Situs": "website",
        "Tanggal Pencatatan": "listing_date",
        "Papan Pencatatan": "board",
        "Bidang Usaha Utama": "main_business",
        "Sektor": "sector",
        "Subsektor": "subsector",
        "Industri": "industry",
        "Subindustri": "subindustry",
        "Biro Administrasi Efek": "share_registrar",
    }
    return translations.get(key.strip(), key.lower().replace(" ", "_").replace(":", ""))


def idx_stock_profile(stock_code: str) -> Dict[str, Any]:
    """Main function for idx-stock skill on Clawhub."""
    # Input sanitization and validation
    stock_code = stock_code.strip().upper()
    if not stock_code or len(stock_code) < 3 or len(stock_code) > 5 or not stock_code.isalnum():
        return {
            "success": False,
            "data": {},
            "message": "Invalid stock code format. Example: BBCA"
        }

    url = f"https://www.idx.co.id/id/perusahaan-tercatat/profil-perusahaan-tercatat/{stock_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.idx.co.id/id/perusahaan-tercatat/profil-perusahaan-tercatat/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cookie": "__cf_bm=example; _ga=example; _gid=example"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        company_data: Dict[str, str] = {}

        # Parse all tables on the page
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:
                    field_name = cells[0].get_text(strip=True)
                    value_cell = cells[2]
                    content = value_cell.get_text(strip=True)
                    if not content and value_cell.find("a"):
                        content = value_cell.find("a").get_text(strip=True)
                    
                    if field_name:
                        english_key = translate_key(field_name)
                        company_data[english_key] = content

        # Add metadata
        company_data["stock_code"] = stock_code
        company_data["source"] = "idx.co.id"
        company_data["scraped_at"] = "live"

        return {
            "success": True,
            "data": company_data,
            "message": f"Profile of {stock_code} successfully retrieved from IDX"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": {},
            "message": f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"Error scraping: {str(e)} (possible page structure changed)"
        }


# For local testing
if __name__ == "__main__":
    result = idx_stock_profile("BBCA")
    print(result)