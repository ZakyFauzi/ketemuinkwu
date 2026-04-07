# 🔑 Ketemuin - Lost & Found NFC Platform

> Platform tracking barang hilang menggunakan teknologi NFC dengan passive tracking dan notifikasi real-time.

Ini adalah proyek untuk kelas **Entrepreneurship** dengan konsep "Lost & Found" yang cerdas menggunakan chip NFC NTAG215.

---

## 🎯 Konsep & Flow

### Untuk Pemilik (Owner):
1. Membeli Ketemuin (gantungan kunci NFC)
2. Pertama kali scan → Halaman unclaimed, dapat Tag ID
3. Go to portal → Aktivasi tag dengan profil (nama, WA, bio, avatar)
4. Create PIN 4-digit
5. Pilih metode notifikasi (Email/Telegram/Keduanya)
6. Selesai! Tag siap dipasang

### Untuk Penemu (Finder):
1. Menemukan Ketemuin yang hilang
2. Scan dengan NFC → Auto-open landing page
3. Lihat profil pemilik (avatar, nama, bio, WhatsApp)
4. Opsi:
   - 💬 Chat WhatsApp langsung
   - 📍 Share GPS location
   - 💭 Pesan anonim di chat

### Backend Logic:
- ✅ Setiap scan → Notifikasi ke pemilik (Email + Telegram Bot)
- ✅ Lokasi ter-capture via browser geolocation API
- ✅ Rate limiting: 1 pesan per scan per IP (prevent spam)
- ✅ Database SQLite menyimpan profile, messages, tracking data

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5 + CSS3 + Vanilla JS (Mobile-First) |
| **Backend** | Flask (Python) |
| **Database** | SQLite3 |
| **Notifications** | Email (SMTP) + Telegram Bot API |
| **Hosting** | Render.com / Railway.app / Heroku |

---

## 📂 Struktur Project

```
ketemuin-development/
├── app.py                      # Backend Flask utama
├── requirements.txt            # Python dependencies
├── database.db               # SQLite database (auto-created)
├── .env.example              # Template environment variables
├── .gitignore                # Git ignore file
├── SETUP.md                  # Panduan setup lengkap
│
└── templates/
    ├── index.html            # Home + Activation form  
    ├── found.html            # Landing page LinkTree-style (untuk finder)
    ├── unclaimed.html        # Halaman jika tag belum diaktivasi
    ├── dashboard.html        # Dashboard untuk pemilik
    ├── admin.html            # Admin panel generate tag
    └── admin_login.html      # Admin login
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone repo
git clone <repo-url>
cd ketemuin-development

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Buat file `.env` berdasarkan `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` dan isi dengan:
- `TELEGRAM_BOT_TOKEN` - Dari @BotFather di Telegram
- `EMAIL_SENDER` - Email pengirim notifikasi
- `EMAIL_PASSWORD` - Password atau App Password (untuk Gmail)
- `SMTP_SERVER` - SMTP server provider email
- `SMTP_PORT` - Port SMTP (biasanya 587)

**📖 [Lihat SETUP.md untuk instruksi detail](./SETUP.md)**

### 3. Run Server

```bash
python app.py
```

Server berjalan di: **http://localhost:5000**

### 4. Test Flow

1. **Admin**: Login ke `/admin` (PIN: 9999)
2. **Generate Tag**: Generate blank NFC tag
3. **Activate**: Buka `/` → Aktivasi tag dengan profil
4. **Finder Scan**: Buka `/found/<tag-id>` untuk simulasi scanner

---

## 🔄 API Routes

### Public Routes

| Route | Method | Desc |
|-------|--------|------|
| `/` | GET | Home page + Activation form |
| `/login` | POST | Login ke dashboard owner |
| `/activate` | POST | Aktivasi tag baru |
| `/found/<tag_id>` | GET | Landing page untuk penemu |
| `/send_message/<tag_id>` | POST | Kirim pesan (finder/owner) |
| `/update_location/<tag_id>` | POST | Update GPS location |

### Admin Routes

| Route | Method | Desc |
|-------|--------|------|
| `/admin` | GET | Admin dashboard |
| `/admin_login` | POST | Login admin |
| `/admin_logout` | GET | Logout admin |
| `/generate_blank` | POST | Generate blank tag |

---

## 📊 Database Schema

### `items` Table - Profil Tag & Pemilik
```sql
id              TEXT PRIMARY KEY        -- Unique Tag ID
item_name       TEXT                    -- Nama barang
pin             TEXT                    -- PIN 4 digit pemilik
owner_name      TEXT                    -- Nama pemilik
owner_whatsapp  TEXT                    -- Nomor WA (untuk penemu)
owner_bio       TEXT                    -- Bio/deskripsi
owner_avatar    TEXT                    -- URL avatar
owner_email     TEXT                    -- Email notifikasi
owner_telegram_id TEXT                  -- Telegram ID untuk bot
notification_method TEXT                -- 'email'|'telegram'|'both'
finder_message  TEXT                    -- Legacy message field
lat, lng        TEXT                    -- Koordinat terakhir
last_scan_timestamp TEXT                -- Waktu scan terakhir
created_at      TEXT                    -- Waktu aktivasi
```

### `messages` Table - Chat Anonim
```sql
id          INTEGER PRIMARY KEY
item_id     TEXT                    -- FK ke items.id
sender      TEXT                    -- 'owner' atau 'finder'
text        TEXT                    -- Isi pesan
timestamp   TEXT                    -- ISO format timestamp
```

### `scan_tracking` Table - Rate Limiting & Analytics
```sql
id          INTEGER PRIMARY KEY
item_id     TEXT                    -- FK ke items.id
ip_address  TEXT                    -- IP penemu
timestamp   TEXT                    -- Waktu scan
action      TEXT                    -- 'location_scan'|'message_sent'
```

---

## 🎨 UI/UX Highlights

### Landing Page (found.html) - LinkTree Style ✨
- **Profile Card** dengan avatar, nama, bio
- **Action Buttons** - WhatsApp chat, GPS share, pesan
- **Chat Anonim** - Rate limited 1x per scan
- **Responsive Design** - Mobile-first, gradient background
- **Smooth Animations** - Slide down, fade in effects

### Admin Generator
- Generate unique Tag ID
- Copy link for NFC writing
- Simple, clean interface

### Activation Form
- Multi-step form dengan visual hierarchy
- Input validation real-time
- Support upload avatar atau use URL
- Double notification (Email + Telegram)

---

## 🔔 Notifikasi Implementation

### Email Notification
```python
send_email_notification(
    email="user@gmail.com",
    subject="🔔 Barangmu Di-scan!",
    message_html="<html>...</html>"
)
```

### Telegram Bot Notification
```python
send_telegram_notification(
    telegram_id="123456789",
    message="🔔 Barangmu baru saja di-scan oleh seseorang!"
)
```

**Features:**
- ✅ HTML formatting di email
- ✅ Maps link untuk lokasi
- ✅ Fallback ke IP location jika GPS ditolak
- ✅ Beautiful HTML template

---

## ⚡ Rate Limiting

Mencegah spam/abuse:
- **1 pesan per scan per IP address**
- **24 hour window** untuk tracking
- Penemu baru dari IP berbeda bisa kirim pesan lagi

```python
can_send = can_send_message(item_id, ip_address)
if not can_send:
    return "⚠️ Kamu sudah mengirim pesan di scan ini", 429
```

---

## 🔐 Security Features

- ✅ PIN protection untuk dashboard pemilik
- ✅ Session management dengan Flask
- ✅ Environment variables untuk sensitive data
- ✅ Anonymous chat (tidak ada exposure nomor WA di chat)
- ✅ IP-based rate limiting
- ✅ Input validation & sanitization

**Recommendations:**
- [ ] Ubah `app.secret_key` dari default ke nilai random
- [ ] Enable HTTPS di production
- [ ] Use CSRF tokens jika ada form
- [ ] Setup firewall rules
- [ ] Monitor logfile untuk abuse attempts

---

## 📱 Mobile Optimization

Semua halaman dioptimasi untuk mobile:
- ✅ Viewport meta tag
- ✅ Flexible grid layout
- ✅ Touch-friendly buttons (min 44px)
- ✅ Readable font sizes
- ✅ Fast loading (no heavy assets)

---

## ☁️ Deployment Options

### 1. **Render.com** ⭐ Recommended
- Free tier dengan 750 hours/month
- Auto-deploy dari GitHub
- Environment variables management
- Auto restart on crash

**[Lihat panduan Render di SETUP.md](./SETUP.md#deployment-ke-cloud)**

### 2. **Railway.app**
- Modern interface
- Pay-as-you-go pricing
- Quick deployment

### 3. **Heroku**
- Classic platform
- Free tier sudah discontinued
- Paid starting $7/month

### 4. **Local + ngrok** (Testing)
```bash
pip install ngrok
ngrok http 5000
```

---

## 🧪 Testing Checklist

### Backend
- [ ] Database initialization (create tables)
- [ ] Activation flow (create item dengan profile)
- [ ] Login & dashboard access
- [ ] Message sending & rate limiting
- [ ] GPS location capture
- [ ] Telegram notification
- [ ] Email notification
- [ ] Admin tag generation

### Frontend
- [ ] Responsive di desktop, tablet, mobile
- [ ] Form validation
- [ ] Chat auto-scroll
- [ ] GPS permission prompt
- [ ] WhatsApp link format
- [ ] Loading states

### Security
- [ ] PIN protection tested
- [ ] Session timeout needed?
- [ ] Rate limiting triggered correctly
- [ ] Env variables loaded properly

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Email tidak terkirim** | Cek SMTP credentials, enable App Password di Gmail |
| **Telegram notif tidak masuk** | Verify TOKEN, check Chat ID format |
| **Rate limit error (429)** | Normal - user hanya bisa 1 pesan per scan |
| **Database locked** | Restart server, check concurrent access |
| **Location not captured** | User denied geolocation permission - show IP fallback |
| **404 on /found/...** | Tag ID tidak valid di database |

---

## 💡 Future Enhancements

- [ ] Admin dashboard untuk analytics (heatmap scan locations)
- [ ] Lost & Found matching algorithm (suggest similar items)
- [ ] Push notifications (PWA/React Native app)
- [ ] Multi-language support
- [ ] Premium features (priority notifications, advanced analytics)
- [ ] QR code + RFID dual support
- [ ] Photo upload untuk barang
- [ ] Review/rating system untuk finder

---

## 📜 License

Proyek untuk Kelas Entrepreneurship - Telkom University 2026

---

## 👨‍💻 Contributing

Buat feature branch, commit changes, push, dan open PR!

```bash
git checkout -b feature/amazing-feature
git commit -am 'Add amazing feature'
git push origin feature/amazing-feature
```

---

## 📞 Support

Pertanyaan atau bug report? Hubungi tim development atau buat issue!

---

**Made with ❤️ by Ketemuin Team @ Telkom University**

Powered by ⚡ Flask, 🤖 Telegram, 📧 SMTP

