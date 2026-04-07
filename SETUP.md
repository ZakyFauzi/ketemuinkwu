# 🚀 Ketemuin Setup Guide

## Persiapan Awal

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🤖 Setup Telegram Bot (Notifikasi Real-Time)

### Langkah 1: Buat Bot di BotFather

1. Buka **Telegram**, cari akun **@BotFather**
2. Ketik command: `/start`
3. Pilih `/newbot` untuk membuat bot baru
4. Ikuti petunjukan:
   - **Give your bot a name**: Contoh: `Ketemuin Bot`
   - **Give your bot a username**: Contoh: `ketemuin_nfc_bot` (harus unik & diakhiri `_bot`)

5. **BotFather akan memberikan Token** - Copy dan simpan!

**Contoh Output:**
```
Done! Congratulations on your new bot. 
You will find it at t.me/ketemuin_nfc_bot. 
You can now add a description, about section and profile picture for your bot, see /help for a list of commands. 

Use this token to access the HTTP API:
123456789:ABCDEfGhIjKlmNoPqRsTuVwXyZ_1234567890AB
```

### Langkah 2: Dapatkan Chat ID Kamu

1. Cari bot mu yang baru dibuat (ketik username di Telegram search)
2. Klik `/start` untuk mulai chat
3. Kirim pesan apapun
4. Buka link ini di browser:
   ```
   https://api.telegram.org/bot123456789:ABCDEfGhIjKlmNoPqRsTuVwXyZ_1234567890AB/getUpdates
   ```
   (Ganti token dengan token mu)

5. Cari di response JSON bagian **"chat":{"id": xxxxx** - Itu adalah Chat ID mu

**Contoh:**
```json
{
  "chat": {
    "id": 987654321,
    "first_name": "Budi"
  }
}
```

### Langkah 3: Set Environment Variables

Kamu punya dua pilihan:

#### **Opsi A: Pakai File `.env` (Recommended)**

Buat file `.env` di folder project:
```
TELEGRAM_BOT_TOKEN=123456789:ABCDEfGhIjKlmNoPqRsTuVwXyZ_1234567890AB
```

Kemudian di `app.py`, tambahkan di bagian atas:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### **Opsi B: Set di Command Line**

```bash
# Windows (PowerShell)
$env:TELEGRAM_BOT_TOKEN = "123456789:ABCDEfGhIjKlmNoPqRsTuVwXyZ_1234567890AB"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="123456789:ABCDEfGhIjKlmNoPqRsTuVwXyZ_1234567890AB"
```

---

## 📧 Setup Email Notifications

### Opsi 1: Gmail (Recommended untuk Pemula)

#### Langkah 1: Enable 2-Factor Authentication
1. Buka https://myaccount.google.com/security
2. Cari **2-Step Verification** - aktifkan jika belum

#### Langkah 2: Buat App Password
1. Ke **https://myaccount.google.com/apppasswords**
2. Pilih:
   - **App**: Mail
   - **Device**: Windows Computer (atau device mu)
3. Google akan generate password 16 karakter - **Copy!**

**Contoh:**
```
abcd efgh ijkl mnop
```

#### Langkah 3: Set Environment Variables

Buat atau update file `.env`:
```
EMAIL_SENDER=emailmu@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

### Opsi 2: Outlook/Hotmail

```
EMAIL_SENDER=emailmu@outlook.com
EMAIL_PASSWORD=password_mu
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

---

### Opsi 3: Custom SMTP Server

```
EMAIL_SENDER=sender@domain.com
EMAIL_PASSWORD=password
SMTP_SERVER=mail.domain.com
SMTP_PORT=587
```

---

## 🎯 Setup User Activation Flow

Ketika user membeli Ketemuin dan scan untuk pertama kali:

1. **Akses unclaimed.html** - Lihat Tag ID mereka
2. **Ke Portal Utama** (`/`) - Pilih "Aktivasi Tag Baru"
3. **Isi Form:**
   - Tag ID (dari kemasan)
   - Nama Barang
   - PIN 4 digit
   - Nama Pemilik
   - Nomor WhatsApp (format: 62812345xxxx)
   - Bio (opsional)
   - Avatar URL (opsional)
   - Email (untuk notifikasi)
   - Telegram ID (opsional - dari chat bot mu)
   - Pilih metode notifikasi (Email/Telegram/Keduanya)

4. **Klik Aktivasi** - User akan redirect ke Dashboard

---

## 🧪 Testing Sebelum Deploy

### Test Telegram Notification
```python
from app import send_telegram_notification

# Ganti 123456789 dengan Chat ID mu
send_telegram_notification(
    telegram_id="123456789",
    message="🔔 Test Notifikasi Telegram dari Ketemuin!"
)
```

### Test Email Notification
```python
from app import send_email_notification

send_email_notification(
    email="emailmu@gmail.com",
    subject="Test Ketemuin",
    message_html="<h1>Test Email OK!</h1>"
)
```

---

## 🚀 Menjalankan Server

```bash
python app.py
```

Server akan berjalan di: **http://localhost:5000**

---

## ☁️ Deployment ke Cloud

### Opsi 1: **Render.com** (Recommended)

1. Push repo ke GitHub
2. Login ke **https://render.com**
3. Create > Web Service
4. Pilih repo mu
5. Set **Start Command**: `gunicorn app:app`
6. Pastikan install dependencies (ganti `requirements.txt`)
7. **Add Environment Variables** di Render dashboard:
   ```
   TELEGRAM_BOT_TOKEN=...
   EMAIL_SENDER=...
   EMAIL_PASSWORD=...
   ```

### Opsi 2: Railway.app

1. Login ke **https://railway.app**
2. New Project > Deploy from GitHub
3. Pilih repo
4. Add Environment Variables dari Render dashboard
5. Railway auto-detect Flask dan deploy

### Opsi 3: Heroku (Gratis tapi terbatas)

```bash
heroku login
heroku create ketemuin-app
git push heroku main
heroku config:set TELEGRAM_BOT_TOKEN=...
```

---

## 📱 LinkTree-Style Landing Page

Halaman `/found/<tag_id>` akan menampilkan:

- ✅ Avatar pemilik
- ✅ Nama pemilik
- ✅ Nama barang
- ✅ Bio/Deskripsi
- ✅ Tombol WhatsApp Chat
- ✅ Tombol Share Location
- ✅ Chat Anonim (Rate Limited 1x per scan)

---

## 🔐 Security Checklist

- [ ] Set PIN Admin yang kuat (bukan "9999")
- [ ] Jangan commit `.env` file ke Git (add ke `.gitignore`)
- [ ] Gunakan HTTPS saat deploy ke production
- [ ] Enable CSRF protection jika perlu
- [ ] Rate limit chat per IP untuk prevent abuse
- [ ] Validate semua input form

---

## 📝 Database Schema

**Tabel `items`:**
```
- id: Tag ID (Primary Key)
- item_name: Nama barang
- pin: PIN pemilik
- owner_name: Nama pemilik
- owner_whatsapp: Nomor WA pemilik
- owner_bio: Bio/deskripsi
- owner_avatar: URL avatar
- owner_email: Email notifikasi
- owner_telegram_id: Telegram ID untuk bot
- notification_method: 'email', 'telegram', 'both'
- lat, lng: Koordinat terakhir
- last_scan_timestamp: Waktu scan terakhir
```

**Tabel `messages`:**
```
- id: Message ID
- item_id: Tag yang bersangkutan
- sender: 'owner' atau 'finder'
- text: Isi pesan
- timestamp: Kapan dikirim
```

**Tabel `scan_tracking`:**
```
- id: Tracking ID
- item_id: Tag yang di-scan
- ip_address: IP penemu
- timestamp: Kapan
- action: 'location_scan', 'message_sent', dll
```

---

## 🆘 Troubleshooting

### Email tidak terkirim
- Cek `EMAIL_SENDER` dan `EMAIL_PASSWORD` sudah benar
- Pastikan 2FA dan App Password sudah di-setup
- Cek SMTP_SERVER dan SMTP_PORT sesuai provider

### Telegram Bot tidak reply
- Pastikan `TELEGRAM_BOT_TOKEN` benar
- Test: `https://api.telegram.org/bot<TOKEN>/getMe` di browser
- Pastikan Chat ID format string "123456789"

### Rate limiting error
- Ini normal! User hanya bisa 1 pesan per scan per IP
- Untuk scan baru dari IP berbeda, bisa kirim pesan lagi

---

Selamat setup! 🎉 Jika ada pertanyaan, tanyakan aja! 

