# Task Planner and Validator (Görev Planlayıcı ve Doğrulayıcı)

Yapay Zeka Ajanları için güvenli, adım adım görev yönetim sistemi.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Özellikler

- **✅ Adım Adım Planlama**: Karmaşık görevleri yönetilebilir adımlara böl
- **🔒 Güvenlik Doğrulama**: Tehlikeli işlemler için yerleşik güvenlik kontrolleri
- **🔄 Geri Alma Desteği**: Başarısız işlemleri geri almak için kontrol noktası sistemi
- **📝 Plan Kalıcılığı**: Planları JSON formatında kaydet ve yükle
- **🎨 Bütünlük Doğrulama**: Müdahaleyi önlemek için SHA-256 kontrol toplamları
- **⚡ Yürütme Kontrolü**: Dry-run modu, otomatik onay ve hata durumunda durdurma seçenekleri
- **📊 İlerleme Takibi**: Gerçek zamanlı durum güncellemeleri ve yürütme özetleri
- **🔍 Detaylı Loglama**: Hata ayıklama ve denetim için kapsamlı loglama

## 🚀 Hızlı Başlangıç

### Kurulum

```bash
# ZIP dosyasını çıkart
unzip task-planner-validator.zip
cd task-planner-validator

# Kurulumu doğrula
python install_check.py

# Testleri çalıştır
python test_basic.py

# Örnekleri deneyin
python examples.py
```

### Temel Kullanım

```python
from task_planner import TaskPlanner

# 1. Planlayıcı oluştur
planner = TaskPlanner(auto_approve=False)

# 2. Yürütücü fonksiyonunu tanımla
def my_executor(action: str, parameters: dict):
    """Adımları çalıştıran fonksiyon"""
    print(f"Çalıştırılıyor: {action}")
    
    if action == "veri_cek":
        return {"veriler": ["Ali", "Ayşe", "Mehmet"]}
    elif action == "veri_isle":
        return {"islendi": True}
    else:
        return {"durum": "tamamlandi"}

# 3. Adımları tanımla
steps = [
    {
        "description": "Veritabanından kullanıcıları çek",
        "action": "veri_cek",
        "parameters": {"limit": 100},
        "expected_output": "Kullanıcı listesi"
    },
    {
        "description": "Kullanıcı verilerini işle",
        "action": "veri_isle",
        "parameters": {"dogrulama": True},
        "expected_output": "İşlenmiş veriler"
    }
]

# 4. Plan oluştur
plan = planner.create_plan(
    title="Kullanıcı Veri İşleme",
    description="Kullanıcı verilerini çek ve işle",
    steps=steps
)

# 5. Planı doğrula
is_valid, warnings = planner.validate_plan(plan)
print(f"Geçerli: {is_valid}")

# 6. Planı onayla
planner.approve_plan(plan, approved_by="admin")

# 7. Planı çalıştır
success, results = planner.execute_plan(plan, my_executor)

# 8. Özet al
summary = planner.get_execution_summary(plan)
print(f"İlerleme: {summary['progress_percentage']:.1f}%")
```

## 📚 Dokümantasyon

- **README.md** - Ana dokümantasyon (İngilizce)
- **SKILL.md** - Kurulum ve kullanım kılavuzu (İngilizce)
- **QUICKSTART.md** - Hızlı başlangıç rehberi (İngilizce)
- **API.md** - Tam API referansı (İngilizce)
- **examples.py** - Kullanım örnekleri
- **test_basic.py** - Test paketi

## 🔧 İleri Düzey Özellikler

### Dry Run (Simülasyon) Modu

Planı çalıştırmadan test et:

```python
success, results = planner.execute_plan(plan, my_executor, dry_run=True)
```

### Otomatik Onay

Manuel onayı atla:

```python
planner = TaskPlanner(auto_approve=True)
```

### Hata Yönetimi

Hata durumunda devam et:

```python
success, results = planner.execute_plan(
    plan, 
    my_executor,
    stop_on_error=False  # Hatalarda devam et
)
```

### Plan Kaydetme

Planları sakla ve tekrar kullan:

```python
# Kaydet
planner.save_plan(plan, "plan.json")

# Yükle
loaded_plan = planner.load_plan("plan.json")

# Bütünlüğü doğrula
if loaded_plan.verify_integrity():
    planner.execute_plan(loaded_plan, my_executor)
```

## 🛡️ Güvenlik Özellikleri

### Tehlikeli İşlem Tespiti

Sistem otomatik olarak tehlikeli işlemleri tespit eder:

```python
steps = [
    {
        "description": "Eski dosyaları sil",
        "action": "dosya_sil",  # ⚠️ Tehlikeli!
        "parameters": {"yol": "/veri/eski"},
        "safety_check": True,  # Uyarı verir
        "rollback_possible": False  # Geri alınamaz
    }
]
```

### Bütünlük Doğrulama

Her plan SHA-256 kontrol toplamı ile korunur:

```python
plan.checksum = plan.calculate_checksum()

if plan.verify_integrity():
    print("✅ Plan bütünlüğü doğrulandı")
```

## 📖 Kullanım Senaryoları

### API Orkestrasyon

```python
steps = [
    {
        "description": "API'ye kimlik doğrulama",
        "action": "api_auth",
        "parameters": {"servis": "github"},
        "expected_output": "Token"
    },
    {
        "description": "Veri çek",
        "action": "api_fetch",
        "parameters": {"endpoint": "/repos"},
        "expected_output": "Repository listesi"
    }
]
```

### Veri Pipeline'ı

```python
steps = [
    {
        "description": "Veri çıkar",
        "action": "extract",
        "parameters": {"kaynak": "veritabani"},
        "expected_output": "Ham veri"
    },
    {
        "description": "Veri dönüştür",
        "action": "transform",
        "parameters": {"kurallar": ["normalize", "validate"]},
        "expected_output": "Temiz veri"
    },
    {
        "description": "Veri yükle",
        "action": "load",
        "parameters": {"hedef": "warehouse"},
        "expected_output": "Başarı onayı"
    }
]
```

## 🤝 Katkıda Bulunma

Katkılar memnuniyetle karşılanır! Lütfen Pull Request göndermekten çekinmeyin.

1. Repository'yi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/HarikaBirOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Harika bir özellik ekle'`)
4. Branch'i push edin (`git push origin feature/HarikaBirOzellik`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- Güvenli, doğrulanmış görev yürütmeye ihtiyaç duyan AI ajanları için tasarlandı
- Workflow orkestrasyon sistemleri ve DevOps en iyi uygulamalarından esinlenildi
- Güvenlik ve güvenilirlik en üst öncelik olarak inşa edildi

## 📞 İletişim

**Yazar**: cerbug45

**GitHub**: [@cerbug45](https://github.com/cerbug45)

## 🚀 Başlarken

1. **install_check.py** çalıştırarak kurulumu doğrulayın
2. **examples.py** ile örneklere bakın
3. **test_basic.py** ile testleri çalıştırın
4. **SKILL.md** dosyasını detaylı kullanım için okuyun

## ⚙️ Gereksinimler

- Python 3.8 veya üzeri
- Harici bağımlılık yok! (Sadece Python standart kütüphanesi)

## 🎯 Proje Yapısı

```
task-planner-validator/
├── task_planner.py      # Ana kütüphane
├── examples.py          # Kullanım örnekleri
├── test_basic.py        # Test paketi
├── install_check.py     # Kurulum doğrulama
├── README.md            # İngilizce dokümantasyon
├── README_TR.md         # Türkçe dokümantasyon (bu dosya)
├── SKILL.md             # Kurulum ve kullanım rehberi
├── QUICKSTART.md        # Hızlı başlangıç
├── API.md              # API referansı
├── LICENSE              # MIT Lisansı
└── requirements.txt     # Bağımlılıklar (yok!)
```

---

⭐ Bu projeyi faydalı buluyorsanız, lütfen GitHub'da yıldız vermeyi düşünün!
