# 🧪 Ketemuin Testing Guide

Testing checklist untuk development dan pre-deployment.

---

## 📋 Setup Awal

Pastikan sudah done:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy .env dari .env.example
cp .env.example .env

# 3. Edit .env dengan credentials kamu
# - TELEGRAM_BOT_TOKEN
# - EMAIL_SENDER & EMAIL_PASSWORD
```

---

## 🚀 Run Server

```bash
python app.py
```

Output should be:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## ✅ Test Scenarios

### **Scenario 1: Activation Flow**

**Step 1:** Admin generates blank tag
```
1. Go to http://localhost:5000/admin
2. Enter PIN: 9999
3. Click "Generate New NFC Tag"
4. Copy the URL (format: http://localhost:5000/found/xxxxxxxx)
5. Note the Tag ID
```

**Expected:** Blank item created in database

---

**Step 2:** User activates tag
```
1. Go to http://localhost:5000/
2. Scroll to "Aktivasi Tag Baru"
3. Fill form:
   - Tag ID: [dari generated tag]
   - Item Name: Kunci Rumah
   - PIN: 1234
   - Owner Name: Budi Santoso
   - WhatsApp: 62812345678
   - Bio: Kunci rumah warna hitam, jangan hilang!
   - Avatar URL: https://via.placeholder.com/100 (opsional)
   - Email: your-email@gmail.com
   - Telegram ID: 987654321 (opsional, skip kalo tidak ada)
   - Notification: Email saja
4. Click "Aktivasi Tag Saya"
```

**Expected:** Redirect ke dashboard dengan greeting message

---

### **Scenario 2: Finder Scan (Landing Page)**

```
1. Go to http://localhost:5000/found/[tag-id-from-above]
2. Verify halaman menampilkan:
   - ✅ Avatar placeholder
   - ✅ Owner name: "Budi Santoso"
   - ✅ Item name: "Kunci Rumah"
   - ✅ Bio text
   - ✅ Green status badge "🔍 Ditemukan"
   - ✅ WhatsApp button (clickable link)
   - ✅ GPS Share button
   - ✅ Chat box
3. Test WhatsApp button:
   - Should open: https://api.whatsapp.com/send?phone=62812345678&text=...
4. Check console untuk notification logs
```

**Expected:** 
- Profile card tampil dengan benar
- Telegram/Email notification terkirim
- Chat section siap untuk input

---

### **Scenario 3: Location Sharing**

```
1. Di finder page (/found/[tag-id])
2. Click "📍 Bagikan Lokasi Saya"
3. Browser akan minta permission geolocation
4. Click "Allow"
5. Status harus berubah jadi "✅ Lokasi berhasil dikirim!"
```

**Expected Behavior:**
- GPS coordinates ter-capture
- Owner dapat email/telegram notification dengan maps link
- Location visible di owner dashboard

**Fallback (Permission Denied):**
- Status: "❌ Izin lokasi ditolak"
- IP address tetap tercatat di database

---

### **Scenario 4: Chat Flow**

**Finder mengirim pesan:**
```
1. Di /found/[tag-id], di chat input: "Halo! Aku menemukan barangmu"
2. Click "Kirim"
3. Pesan harus muncul di chat sebagai "finder" (green bubble)
```

**Rate Limiting Test:**
```
1. Try kirim pesan lagi dari browser sama
2. Harus error: "⏳ Kamu sudah mengirim pesan..."
3. Try dari device/IP lain → bisa kirim
```

**Owner mebalas:**
```
1. Owner login ke dashboard: http://localhost:5000/login
   - Tag ID: [sama]
   - PIN: 1234
2. Di dashboard, lihat chat → reply pesan
3. Pesan owner harus muncul sebagai "owner" (hijau)
```

---

### **Scenario 5: Notification Testing**

#### **Email Notification**
```python
# Run di Python interactive shell atau buat test_notif.py:
from app import send_email_notification

result = send_email_notification(
    email="your-email@gmail.com",
    subject="Test Email from Ketemuin",
    message_html="<h1>Test OK! ✅</h1>"
)

print("Email sent:", result)
```

**Expected:** Email terkirim dalam 1-2 detik

#### **Telegram Notification**
```python
from app import send_telegram_notification

result = send_telegram_notification(
    telegram_id="987654321",
    message="<b>Test Notifikasi Telegram</b>\nDari Ketemuin! ✅"
)

print("Telegram sent:", result)
```

**Expected:** Message terkirim ke Telegram chat dengan mu

---

### **Scenario 6: Dashboard Owner**

```
1. Owner login: /login
   - Tag ID: [activated-tag]
   - PIN: 1234
2. Dashboard should show:
   - ✅ Location card (jika udah ada)
   - ✅ Chat history
   - ✅ Reply form
3. Click "🗺️ Buka di Google Maps" (jika ada location)
4. Verify maps link format benar
```

---

## 🐛 Debug Checklist

### Database Issues
```bash
# Check database:
sqlite3 database.db ".tables"
# Should show: items, messages, scan_tracking

# Check items:
sqlite3 database.db "SELECT id, owner_name, item_name FROM items;"

# Check messages:
sqlite3 database.db "SELECT * FROM messages;"

# Delete database untuk fresh start:
rm database.db
# Server akan recreate on next run
```

### Environment Variables
```python
# Di Python shell:
import os
from dotenv import load_dotenv
load_dotenv()

print("TELEGRAM_TOKEN:", os.getenv('TELEGRAM_BOT_TOKEN'))
print("EMAIL_SENDER:", os.getenv('EMAIL_SENDER'))
print("SMTP_SERVER:", os.getenv('SMTP_SERVER'))
```

### Flask Debug Logs
```
# Server berjalan dengan debug=True, jadi lihat output untuk:
- POST /activate [201 CREATED]
- GET /found/xxx [200 OK]
- POST /send_message [302 REDIRECT]
- POST /update_location [200 OK]

# Error 404 = Wrong tag ID atau halaman tidak ada
# Error 403 = Wrong PIN
# Error 429 = Rate limit triggered
```

---

## 📊 Data Verification

### Check Profile di Database
```bash
sqlite3 database.db "SELECT id, owner_name, owner_whatsapp, owner_email, notification_method FROM items WHERE id='xxx';"
```

### Check Messages
```bash
sqlite3 database.db "SELECT sender, text, timestamp FROM messages WHERE item_id='xxx' ORDER BY id DESC LIMIT 10;"
```

### Check Scan Tracking
```bash
sqlite3 database.db "SELECT * FROM scan_tracking WHERE item_id='xxx';"
```

---

## 🔐 Security Testing

### 1. PIN Protection
```
1. Go to /login
2. Enter wrong PIN → Should fail "Login Gagal"
3. Enter correct PIN → Redirect ke dashboard
```

### 2. Rate Limiting
```
1. Send message dari IP A
2. Try send lagi dari IP A → Error 429
3. Simulate different IP (use ngrok atau proxy)
4. Should bisa send message lagi
```

### 3. Admin PIN
```
1. Try /admin tanpa login → Redirect ke admin_login.html
2. Wrong PIN → Error 403
3. Correct PIN (9999) → Admin dashboard
```

---

## 🧬 Test Scripts

### test_notifications.py
```python
#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from app import send_telegram_notification, send_email_notification
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 50)
print("KETEMUIN NOTIFICATION TEST")
print("=" * 50)

# Test Email
email = os.getenv('EMAIL_SENDER')
print(f"\n📧 Testing Email Notification to {email}...")
email_result = send_email_notification(
    email=email,
    subject="Test Ketemuin Email",
    message_html="<h1>✅ Email Test OK!</h1>"
)
print(f"Result: {'✅ SENT' if email_result else '❌ FAILED'}")

# Test Telegram
telegram_id = input("\n🤖 Enter Telegram ID (or skip): ")
if telegram_id:
    print(f"Testing Telegram Notification to {telegram_id}...")
    tg_result = send_telegram_notification(
        telegram_id=telegram_id,
        message="<b>✅ Telegram Test OK!</b>"
    )
    print(f"Result: {'✅ SENT' if tg_result else '❌ FAILED'}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
```

Run: `python test_notifications.py`

---

## ✨ Pre-Deployment Checklist

- [ ] All scenarios tested locally
- [ ] Notifications working (email + telegram)
- [ ] Database operations verified
- [ ] Rate limiting triggered correctly
- [ ] Forms validate properly
- [ ] Mobile responsive (test di phone)
- [ ] No console errors (F12)
- [ ] .env file tidak dicommit ke Git
- [ ] requirements.txt updated
- [ ] SETUP.md & README.md complete
- [ ] Admin PIN changed dari default
- [ ] Environment variables set di platform deployment

---

## 🚀 Ready to Deploy?

Jika semua ✅, siap untuk:
1. Push ke GitHub
2. Deploy ke Render/Railway/Heroku
3. Set environment variables di cloud platform
4. Test production URL

See SETUP.md for deployment instructions.

