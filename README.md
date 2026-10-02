# 🔍 LinkedIn Job Scraper Bot

Bot Python untuk scraping data lowongan kerja dari LinkedIn secara otomatis dengan notifikasi ke Telegram.

## ✨ Fitur

- 🔎 Scrape lowongan kerja dari LinkedIn (tanpa perlu login)
- 📊 Export data ke CSV / Excel
- 📱 Notifikasi otomatis ke Telegram
- ⏰ Mode terjadwal (auto scraping berkala)
- 🔑 Filter berdasarkan keyword & lokasi
- 🛡️ Anti rate-limiting (random delay, retry, rotating user-agent)

## 📁 Struktur Project

```
new_project/
├── main.py           # Entry point utama
├── scraper.py        # Core scraper LinkedIn
├── exporter.py       # Export ke CSV/Excel
├── notifier.py       # Notifikasi Telegram
├── config.py         # Konfigurasi dari .env
├── requirements.txt  # Dependencies
├── .env.example      # Template environment variables
└── output/           # Folder hasil scraping
```

## 🚀 Cara Pakai

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Konfigurasi

Copy file `.env.example` ke `.env` dan isi dengan konfigurasi kamu:

```bash
copy .env.example .env
```

Edit file `.env`:

```env
# Telegram Bot (optional - bisa dikosongkan kalau belum mau pakai)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Keyword pencarian (pisahkan dengan koma)
SEARCH_KEYWORDS=python developer,data analyst,software engineer

# Lokasi
SEARCH_LOCATION=Indonesia

# Interval scraping (menit)
SCRAPE_INTERVAL_MINUTES=60
```

### 3. Jalankan Bot

**Scrape sekali:**
```bash
python main.py
```

**Scrape terjadwal (otomatis setiap X menit):**
```bash
python main.py --schedule
```

**Custom keyword & lokasi:**
```bash
python main.py --keywords "data engineer,backend developer" --location "Jakarta"
```

## 📱 Setup Telegram Bot

1. Buka Telegram, cari **@BotFather**
2. Kirim `/newbot` dan ikuti instruksinya
3. Copy **Bot Token** yang diberikan
4. Untuk mendapatkan **Chat ID**:
   - Kirim pesan ke bot kamu
   - Buka: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Cari `"chat":{"id": XXXXXXX}` - itu Chat ID kamu
5. Masukkan token & chat ID ke file `.env`

## 📊 Contoh Output CSV

| title | company | location | date_posted | job_url |
|-------|---------|----------|-------------|---------|
| Python Developer | PT ABC | Jakarta | 2 hours ago | https://linkedin.com/jobs/... |
| Data Analyst | Gojek | Jakarta | 1 day ago | https://linkedin.com/jobs/... |

## ⚠️ Disclaimer

Bot ini hanya mengakses data **publik** dari LinkedIn (halaman guest/tanpa login). Gunakan secara bijak dan patuhi Terms of Service LinkedIn. Jangan scrape terlalu agresif.
