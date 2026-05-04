# 🌱 FoodCycle AI — Smart Surplus Food Ecosystem

> Platform cerdas berbasis web untuk mengelola stok bahan makanan, mendapatkan rekomendasi resep berbasis AI, dan mendistribusikan surplus pangan lokal.

**Kelompok 5 — Proyek Perangkat Lunak A**  
Departemen Informatika, Fakultas MIPA, Universitas Syiah Kuala — 2026

---

## 📌 Tentang Proyek

FoodCycle AI adalah platform web yang mengintegrasikan kecerdasan buatan (AI) dengan ekosistem pertukaran surplus pangan lokal. Platform ini merespons permasalahan *food waste* yang semakin mendesak, di mana sepertiga produksi pangan dunia terbuang sia-sia setiap tahunnya (FAO, 2019).

### Kontribusi terhadap SDGs
- **SDG 12** — Konsumsi dan Produksi yang Bertanggung Jawab
- **SDG 13** — Penanganan Perubahan Iklim

---

## 👥 Tim Pengembang

| Nama | NIM | Role |
|------|-----|------|
| Rahmatun Nisa | 2308107010016 | AI & Logic |
| Haikal Aulia | 2308107010063 | QA & Deploy|
| Dwi Hamdan Sukran | 2308107010065 | Frontend |
| Aska Shahira | 2308107010075 | Backend & Database + Integration |

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🔐 **Autentikasi** | Register, Login, Logout dengan enkripsi password bcrypt |
| 📦 **Manajemen Stok** | CRUD bahan makanan dengan notifikasi near-expiry |
| 🤖 **Resep AI** | Rekomendasi resep dari Groq API (LLaMA 3.3 70B) berdasarkan stok |
| 🗺️ **Surplus Exchange** | Marketplace surplus dengan peta interaktif Leaflet.js + filter radius Haversine |
| 📝 **Buat Listing** | Upload surplus untuk dijual atau didonasikan |
| ⭐ **Review & Rating** | Sistem ulasan dan rating antar pengguna |
| 📊 **Dashboard** | Statistik stok, dampak lingkungan, dan aktivitas |
| 👤 **Profil Publik** | Halaman profil yang bisa dilihat pengguna lain |
| ⚙️ **Admin Panel** | Dashboard admin dengan chart, moderasi listing, manajemen pengguna |
| 📬 **Pesanan Masuk** | Penjual bisa accept/reject pesanan |

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Backend** | Django 5.2 (Python) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | HTML, CSS, JavaScript (Django Templates) |
| **AI API** | Groq API — LLaMA 3.3 70B |
| **Peta** | Leaflet.js + OpenStreetMap |
| **Font** | Fraunces + Plus Jakarta Sans (Google Fonts) |
| **Chart** | Chart.js |
| **Auth** | Django built-in + bcrypt |

---

## 📁 Struktur Proyek

```
FoodCycle_AI/
├── accounts/          # Auth, profil, admin views
├── food/              # Stok bahan, resep AI
├── surplus/           # Listing, transaksi, review
├── templates/         # Semua HTML templates
│   ├── accounts/
│   ├── food/
│   └── surplus/
├── static/
│   └── css/
│       └── style.css
├── foodcycle/         # Settings, URLs utama
├── manage.py
├── requirements.txt
└── .env               # Tidak di-push (lihat .env.example)
```

---

## 🚀 Cara Menjalankan (Development)

### Prerequisites
- Python 3.10+
- pip

### Langkah Instalasi

**1. Clone repository:**
```bash
git clone  https://github.com/askashahira/FoodCycle_AI-Kelompok5.git
cd foodcycle-ai
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Buat file `.env`** di root folder:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GROQ_API_KEY=your-groq-api-key
DEEPSEEK_API_KEY=isi-nanti
```

> Dapatkan Groq API Key gratis di: https://console.groq.com

**4. Jalankan migrasi:**
```bash
python manage.py migrate
```

**5. Buat superuser (admin):**
```bash
python manage.py createsuperuser
```

**6. Jalankan server:**
```bash
python manage.py runserver
```

**7. Buka browser:** http://127.0.0.1:8000

---

## 🌐 Cara Deploy (Production)

Platform ini siap di-deploy ke **Railway** atau **Render**.

### Deploy ke Railway

**1. Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

**2. Tambah dependensi production di `requirements.txt`:**
```
gunicorn
whitenoise
psycopg2-binary
dj-database-url
```

**3. Buat `Procfile`** di root:
```
web: gunicorn foodcycle.wsgi --log-file -
```

**4. Update `foodcycle/settings.py`** untuk production:
```python
import dj_database_url
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**5. Collect static:**
```bash
python manage.py collectstatic --noinput
```

**6. Push & deploy:**
```bash
railway init
railway up
```

**7. Set environment variables di Railway dashboard:**
```
SECRET_KEY=your-production-secret-key
DEBUG=False
GROQ_API_KEY=your-groq-api-key
```

**8. Jalankan migrasi di Railway:**
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

### Deploy ke Render (Alternatif)

**1. Buat `render.yaml`** di root:
```yaml
services:
  - type: web
    name: foodcycle-ai
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn foodcycle.wsgi
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: GROQ_API_KEY
        sync: false
```

**2.** Push ke GitHub, lalu connect repository di https://render.com

---

## 🔑 Environment Variables

| Variable | Deskripsi | Required |
|----------|-----------|----------|
| `SECRET_KEY` | Django secret key | ✅ |
| `DEBUG` | True/False | ✅ |
| `GROQ_API_KEY` | API key dari console.groq.com | ✅ |
| `DATABASE_URL` | URL database production | Production only |
| `DEEPSEEK_API_KEY` | Alternatif AI API | ❌ |

---

## 📱 Halaman Aplikasi

| URL | Halaman |
|-----|---------|
| `/` | Landing Page |
| `/accounts/register/` | Registrasi |
| `/accounts/login/` | Login |
| `/dashboard/` | Dashboard User |
| `/stok/` | Manajemen Stok Bahan |
| `/resep/` | Rekomendasi Resep AI |
| `/surplus/` | Surplus Exchange + Peta |
| `/surplus/buat/` | Buat Listing |
| `/surplus/listing-saya/` | Listing Saya |
| `/surplus/pembelian-saya/` | Pembelian Saya |
| `/surplus/pesanan-masuk/` | Pesanan Masuk (Penjual) |
| `/accounts/profil/` | Profil Saya |
| `/accounts/admin-dashboard/` | Admin Panel |

---

## 📸 Screenshots

> *(Tambahkan screenshot aplikasi di sini)*

---

## 📚 Referensi

- FAO. (2019). *The State of Food and Agriculture*. Rome: FAO.
- UNEP. (2021). *Food Waste Index Report 2021*. Nairobi: UNEP.
- Klerkx et al. (2019). Digital agriculture, smart farming and agriculture 4.0. *NJAS*.
- Stöckli et al. (2018). Interventions to prevent consumer food waste. *Resources, Conservation and Recycling*.
- The Guardian. (2025). AI Tool Trial Could Save Equivalent of 1.5m Meals in Food Waste.

---

## 📄 Lisensi

Proyek ini dibuat untuk memenuhi tugas mata kuliah Proyek Perangkat Lunak A, Departemen Informatika, Universitas Syiah Kuala, 2026.

---

*🌱 FoodCycle AI — Kurangi Food Waste, Mulai dari Dapurmu*
