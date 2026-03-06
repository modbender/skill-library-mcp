---
name: ai_c_plan
description: "AI-C plan klasöründeki MD/CSV planı okuyup dependency sırasına göre tamamen otomatik ilerler; geliştirir, test eder, raporlar."
---

Proje ve structure yapısını oluştur. Gerekli dosyaları oluştur. Teknoloji stack ve design referanslarına uygun şekilde kod yaz. Her step'te planlanan değişiklikleri uygula, test et, raporla. Gerektiğinde config dosyaları oluştur. Her step sonunda commit at. Eğer bir step eksik bilgi/erişim/bağımlılık nedeniyle yapılamıyorsa Blocked yap ve gereken aksiyonları açıkla.

# PRE-EXECUTION RULE
Her step başlamadan önce:
1. docs/architecture/AI_CONSULTANT_SYSTEM_PROMPT.md dosyasını oku
2. Bu dokümandaki teknoloji stack ve monorepo yapısına uyduğunu doğrula
3. Uymuyorsa step'i Blocked yap ve sapma nedenini açıkla
 3.1 Minimum sapmayla uyumlandırmayı dene.
 3.2 Gerekirse config dosyası üret.
 3.3 Gerçekten imkansızsa Blocked yap.
4.Eksik klasörleri ve minimal dosyaları otomatik oluştur (packages/config gibi) ve devam et; sadece destructive işlemlerde dur.
5. UI step başlamadan önce `/home/adige/AI-C/desing` klasöründeki ilgili ekran görseli/HTML dosyasını incele ve ekranı referansla birebir hizala.
6. Database/schema değişikliği yapılıyorsa migration üret ve uygula.


## ENV POLICY (No-Questions Mode)
Bu projede dış bağımlılıklar için tüm konfigürasyon .env üzerinden yönetilecek.

Kurallar:
1) Agent gerçek secret üretmeye/uydurmaya çalışmaz.
2) Agent her servis için .env.example ve ilgili alt-app .env.example dosyalarını oluşturur/günceller.
3) Gerçek secret gerekli ise placeholder bırakır (örn: "REPLACE_ME") ve açıklama ekler.
4) Eksik secret varsa:
   - Mümkünse "DEV_FALLBACK" moduna geç (mock provider / stub).
   - Uygulama boot edebilecek kadar default ile ilerle.
   - Sadece tamamen imkânsızsa Blocked yap.
5) Tüm dış servis konfigürasyonları .env üzerinden yönetilir.
6) .env.example dosyaları otomatik oluşturulur/güncellenir.
7) Gerçek secret üretilmez, placeholder bırakılır.
8) Eksik secret varsa DEV_FALLBACK_MODE ile mock provider kullanılır.

Zorunlu dosyalar:
- .env.example (repo root)
- apps/api/.env.example
- apps/web/.env.example
- apps/mobile/.env.example

Git kuralları:
- .env* dosyalarını gitignore et (sadece *.example commit edilir).

# Autopilot Modu
Bu skill, kullanıcıdan her adımda onay istemeden ilerler.
Sadece şu durumlarda durur:
- Bir step "Blocked" olursa (eksik bilgi/erişim/bağımlılık).
- Güvenli olmayan/destructive bir işlem gerekiyorsa (silme, prod deploy, ödeme, gizli anahtar yazma).
- Plan dosyaları bulunamazsa.

## Plan Kaynakları (öncelik)
1) `plan/ai_consultant_mobile_project_plan.md`
2) Yoksa `plan/ai_consultant_full_project_plan.md`
3) Md yoksa csv fallback dosyaları

## Yürütme Algoritması
1) Planı oku → tüm ST-* satırlarını çıkar.
2) Bir DAG oluştur:
   - `depends` tamamlanmadan step başlamaz.
   - `blocks` bir sonraki hedefi gösterir (sıra/öncelik ipucu).
3) Çalıştırma sırası:
   - Önce P0'lar, sonra P1/P2/P3
   - Aynı öncelikte dependency-ready olanları sırayla
4) Her step için:
   - "Planlanan değişiklik" (kısa)
   - Uygulama: dosya değişiklikleri
   - Komutlar: lint/test/build (repo yapısına göre)
   - Schema değişikliği varsa: Prisma migration (`apps/api` içinde) + migration dosyaları
   - Doğrulama: acceptance kriteri yerine "plan hedefi + çalışır build/test"
   - Status: Done / Blocked
   - Blocked ise: neden + gereken aksiyonlar + hangi bilgi lazım
5) Her tamamlanan step sonunda:
  - git add .
  - Conventional Commit formatında commit at
  - Commit mesajı: "feat(epic-01): initialize monorepo structure"

## Repo/Çalışma Kuralları
- Workspace dışına yazma.
- Gizli anahtarları (API key, cert, signing key) dosyaya yazma; sadece env değişkeni olarak tarif et.
- Progress kaydı tek kaynak olarak `/home/adige/AI-C/progress.json` üzerinde tutulur.
- Bir step tamamlandığında ilgili step status alanını `done`/`DONE` olarak güncelle.
- Kullanıcıdan onay istemeden sıradaki runnable maddeye geç.
- Her 3-5 step’te bir veya büyük bir değişiklikte:
  - `git status` kontrol et
  - mümkünse küçük commit at (repo git ise)
- Eğer repo yoksa güvenli şekilde `git init` yap ve devam et.

## Çıktı Formatı
Her step için:

### Step <ID>: <Title>
- Priority:
- Depends:
- Changes:
- Files changed:
- Commands run:
- Verification:
- Status: Done/Blocked
