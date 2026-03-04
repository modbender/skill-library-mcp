"""
AI Ajanları İçin Yardımcı Araçlar Kütüphanesi
AI ajanlarının görevlerini yerine getirmek için kullanabileceği fonksiyonlar
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib


class FileTools:
    """Dosya işlemleri için araçlar"""
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """Dosya içeriğini oku"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Hata: {str(e)}"
    
    @staticmethod
    def write_file(filepath: str, content: str) -> str:
        """Dosyaya yaz"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Başarılı: {filepath} yazıldı"
        except Exception as e:
            return f"Hata: {str(e)}"
    
    @staticmethod
    def list_files(directory: str = ".", extension: Optional[str] = None) -> List[str]:
        """Dizindeki dosyaları listele"""
        try:
            files = os.listdir(directory)
            if extension:
                files = [f for f in files if f.endswith(extension)]
            return files
        except Exception as e:
            return [f"Hata: {str(e)}"]
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Dosya var mı kontrol et"""
        return os.path.exists(filepath)


class TextTools:
    """Metin işleme araçları"""
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Metinden email adreslerini çıkar"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Metinden URL'leri çıkar"""
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Metinden telefon numaralarını çıkar"""
        pattern = r'\b(?:\+90|0)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def word_count(text: str) -> int:
        """Kelime sayısını hesapla"""
        return len(text.split())
    
    @staticmethod
    def summarize_text(text: str, max_length: int = 100) -> str:
        """Metni özetle (basit kesme)"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Fazla boşlukları temizle"""
        return ' '.join(text.split())


class DataTools:
    """Veri işleme araçları"""
    
    @staticmethod
    def save_json(data: Any, filepath: str) -> str:
        """Veriyi JSON olarak kaydet"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return f"Başarılı: {filepath} kaydedildi"
        except Exception as e:
            return f"Hata: {str(e)}"
    
    @staticmethod
    def load_json(filepath: str) -> Any:
        """JSON dosyasını yükle"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def csv_to_dict(csv_text: str) -> List[Dict[str, str]]:
        """CSV metnini sözlük listesine çevir"""
        lines = csv_text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = [h.strip() for h in lines[0].split(',')]
        result = []
        
        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            if len(values) == len(headers):
                result.append(dict(zip(headers, values)))
        
        return result
    
    @staticmethod
    def dict_to_csv(data: List[Dict[str, Any]]) -> str:
        """Sözlük listesini CSV'ye çevir"""
        if not data:
            return ""
        
        headers = list(data[0].keys())
        lines = [','.join(headers)]
        
        for row in data:
            values = [str(row.get(h, '')) for h in headers]
            lines.append(','.join(values))
        
        return '\n'.join(lines)


class UtilityTools:
    """Genel yardımcı araçlar"""
    
    @staticmethod
    def get_timestamp() -> str:
        """Şu anki zaman damgasını al"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def generate_id(text: str) -> str:
        """Metinden benzersiz ID oluştur"""
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    @staticmethod
    def calculate_percentage(part: float, whole: float) -> float:
        """Yüzde hesapla"""
        if whole == 0:
            return 0.0
        return round((part / whole) * 100, 2)
    
    @staticmethod
    def safe_divide(a: float, b: float, default: float = 0.0) -> float:
        """Güvenli bölme (sıfıra bölme hatası vermez)"""
        if b == 0:
            return default
        return a / b


class MemoryTools:
    """Hafıza yönetimi araçları"""
    
    def __init__(self):
        self.memory: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any) -> str:
        """Bir değeri hafızaya kaydet"""
        self.memory[key] = value
        return f"'{key}' kaydedildi"
    
    def retrieve(self, key: str) -> Any:
        """Hafızadan bir değer al"""
        return self.memory.get(key, None)
    
    def delete(self, key: str) -> str:
        """Hafızadan bir değer sil"""
        if key in self.memory:
            del self.memory[key]
            return f"'{key}' silindi"
        return f"'{key}' bulunamadı"
    
    def list_keys(self) -> List[str]:
        """Tüm anahtarları listele"""
        return list(self.memory.keys())
    
    def clear(self) -> str:
        """Tüm hafızayı temizle"""
        self.memory.clear()
        return "Hafıza temizlendi"


class ValidationTools:
    """Doğrulama araçları"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Email geçerli mi kontrol et"""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """URL geçerli mi kontrol et"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Telefon numarası geçerli mi (Türkiye formatı)"""
        pattern = r'^(?:\+90|0)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        return bool(re.match(pattern, phone))


# Kullanım örneği
if __name__ == "__main__":
    print("=== AI Ajanları İçin Araçlar Kütüphanesi ===\n")
    
    # Dosya araçları örneği
    print("1. Dosya Araçları:")
    FileTools.write_file("test.txt", "Merhaba AI Ajanı!")
    content = FileTools.read_file("test.txt")
    print(f"   Okunan içerik: {content}")
    
    # Metin araçları örneği
    print("\n2. Metin Araçları:")
    text = "İletişim: ali@example.com, tel: 0532 123 45 67"
    emails = TextTools.extract_emails(text)
    phones = TextTools.extract_phone_numbers(text)
    print(f"   Bulunan emailler: {emails}")
    print(f"   Bulunan telefonlar: {phones}")
    
    # Veri araçları örneği
    print("\n3. Veri Araçları:")
    data = [
        {"isim": "Ali", "yaş": "25"},
        {"isim": "Ayşe", "yaş": "30"}
    ]
    csv = DataTools.dict_to_csv(data)
    print(f"   CSV çıktısı:\n{csv}")
    
    # Yardımcı araçlar örneği
    print("\n4. Yardımcı Araçlar:")
    timestamp = UtilityTools.get_timestamp()
    print(f"   Şu anki zaman: {timestamp}")
    
    # Hafıza araçları örneği
    print("\n5. Hafıza Araçları:")
    memory = MemoryTools()
    memory.store("kullanıcı_adı", "Ahmet")
    print(f"   Kaydedilen değer: {memory.retrieve('kullanıcı_adı')}")
    
    # Doğrulama araçları örneği
    print("\n6. Doğrulama Araçları:")
    print(f"   Email geçerli mi: {ValidationTools.is_valid_email('test@example.com')}")
    print(f"   URL geçerli mi: {ValidationTools.is_valid_url('https://google.com')}")
    
    print("\n✓ Tüm araçlar test edildi!")
