from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
import sqlite3
import uuid
import requests
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'kunci_rahasia_kewirausahaan_2026')

# ==========================================
# KONFIGURASI NOTIFIKASI
# ==========================================
# TELEGRAM BOT
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE').strip()
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

# EMAIL SMTP
EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'noreply@ketemuin.id').strip()
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_email_password').replace(' ', '').strip()
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))


def notifications_ready():
    telegram_ready = TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'
    email_ready = (
        EMAIL_SENDER
        and EMAIL_PASSWORD
        and EMAIL_SENDER != 'noreply@ketemuin.id'
        and EMAIL_PASSWORD != 'your_email_password'
    )
    return telegram_ready, email_ready


def ensure_column(c, table_name, column_name, column_def):
    c.execute(f"PRAGMA table_info({table_name})")
    existing_cols = [row[1] for row in c.fetchall()]
    if column_name not in existing_cols:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")


def migrate_db(c):
    # Backward compatible migration for old databases.
    ensure_column(c, 'items', 'owner_name', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'owner_whatsapp', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'owner_bio', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'owner_avatar', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'owner_email', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'owner_telegram_id', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'notification_method', "TEXT DEFAULT 'email'")
    ensure_column(c, 'items', 'last_scan_timestamp', "TEXT DEFAULT ''")
    ensure_column(c, 'items', 'created_at', "TEXT DEFAULT ''")
    ensure_column(c, 'messages', 'timestamp', "TEXT DEFAULT ''")

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Tabel items - dengan profil owner
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            item_name TEXT,
            pin TEXT,
            owner_name TEXT,
            owner_whatsapp TEXT,
            owner_bio TEXT,
            owner_avatar TEXT,
            owner_email TEXT,
            owner_telegram_id TEXT,
            notification_method TEXT,
            finder_message TEXT,
            lat TEXT,
            lng TEXT,
            last_scan_timestamp TEXT,
            created_at TEXT
        )
    ''')
    
    # Tabel messages - dengan timestamp
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            sender TEXT,
            text TEXT,
            timestamp TEXT
        )
    ''')
    
    # Tabel scan tracking - untuk rate limiting
    c.execute('''
        CREATE TABLE IF NOT EXISTS scan_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            ip_address TEXT,
            timestamp TEXT,
            action TEXT
        )
    ''')

    migrate_db(c)
    
    conn.commit()
    conn.close()

init_db()

# ==========================================
# HELPER FUNCTIONS - NOTIFIKASI
# ==========================================

def send_telegram_notification(telegram_id, message):
    """Kirim notifikasi via Telegram Bot"""
    if not telegram_id or telegram_id == '':
        print('[NOTIFY][TELEGRAM] skipped: empty telegram id')
        return False
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print('[NOTIFY][TELEGRAM] skipped: TELEGRAM_BOT_TOKEN belum valid')
        return False
    
    try:
        payload = {
            'chat_id': telegram_id.strip(),
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=5)
        ok = response.status_code == 200
        if not ok:
            print(f"[NOTIFY][TELEGRAM] failed {response.status_code}: {response.text}")
        else:
            print('[NOTIFY][TELEGRAM] success')
        return ok
    except Exception as e:
        print(f"[NOTIFY][TELEGRAM] error: {e}")
        return False

def send_email_notification(email, subject, message_html):
    """Kirim notifikasi via Email"""
    if not email or email == '':
        print('[NOTIFY][EMAIL] skipped: empty target email')
        return False
    if not EMAIL_SENDER or not EMAIL_PASSWORD or EMAIL_PASSWORD == 'your_email_password':
        print('[NOTIFY][EMAIL] skipped: EMAIL_SENDER/EMAIL_PASSWORD belum valid')
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = email
        
        msg.attach(MIMEText(message_html, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print('[NOTIFY][EMAIL] success')
        return True
    except Exception as e:
        print(f"[NOTIFY][EMAIL] error: {e}")
        return False

def notify_owner(item, coords_lat=None, coords_lng=None):
    """Notify owner ketika barang di-scan"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Catat scan dalam tracking
    ip = request.remote_addr
    c.execute(
        'INSERT INTO scan_tracking (item_id, ip_address, timestamp, action) VALUES (?, ?, ?, ?)',
        (item[0], ip, datetime.now().isoformat(), 'location_scan')
    )
    conn.commit()
    conn.close()
    
    item_id = item[0]
    item_name = item[1]
    owner_name = item[3]
    location_info = ""
    
    if coords_lat and coords_lng:
        maps_link = f"https://www.google.com/maps?q={coords_lat},{coords_lng}"
        location_info = f"\n📍 <b>Lokasi:</b> <a href='{maps_link}'>Lihat di Maps</a>"
    
    telegram_ready, email_ready = notifications_ready()

    # Telegram Message
    base_url = request.host_url.rstrip('/')
    info_link = f"{base_url}/found/{item_id}"
    telegram_message = (
        f"🔔 <b>Notifikasi Ketemuin!</b>\n\n"
        f"<b>{item_name}</b> kamu baru saja di-scan oleh seseorang! 👀\n"
        f"Penemu bisa menghubungimu melalui portal kami.\n"
        f"{location_info}\n\n"
        f"🔗 Buka halaman tag: {info_link}"
    )
    
    # Email Message
    email_subject = f"🔔 {item_name} Kamu Di-scan! - Ketemuin"
    email_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background: #f4f7f6; padding: 20px;">
            <div style="background: white; padding: 25px; border-radius: 12px; max-width: 500px; margin: auto;">
                <h2 style="color: #27ae60;">🔔 Notifikasi Ketemuin</h2>
                <p style="font-size: 16px;">Halo <b>{owner_name}</b>,</p>
                
                <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #27ae60; margin: 20px 0;">
                    <p style="margin: 0; font-size: 18px;"><b>{item_name}</b> kamu baru saja di-scan oleh seseorang! 👀</p>
                </div>
                
                <p>Penemu dapat menghubungimu melalui portal kami. Mereka bisa mengirim lokasi dan berkomunikasi anonim denganmu.</p>
                
                {f'<p>📍 <b>Lokasi:</b> <a href="{maps_link}" style="color: #3498db;">Lihat di Google Maps</a></p>' if coords_lat else '<p>⏳ Lokasi belum dibagikan.</p>'}
                
                <a href="{info_link}" style="display: inline-block; background: #27ae60; color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; margin-top: 15px;">
                    ➡️ Cek Dashboard
                </a>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #7f8c8d;">Pesan ini dikirim oleh sistem Ketemuin secara otomatis.</p>
            </div>
        </body>
    </html>
    """
    
    # Send notifications based on preference
    notification_method = item[9] if len(item) > 9 else 'both'
    
    sent_telegram = False
    sent_email = False
    
    if notification_method in ['telegram', 'both'] and telegram_ready:
        sent_telegram = send_telegram_notification(item[8], telegram_message)  # owner_telegram_id

    if notification_method in ['email', 'both'] and email_ready:
        sent_email = send_email_notification(item[7], email_subject, email_html)  # owner_email

    if notification_method in ['telegram', 'both'] and not telegram_ready:
        print('[NOTIFY] telegram diminta tapi belum configured')

    if notification_method in ['email', 'both'] and not email_ready:
        print('[NOTIFY] email diminta tapi belum configured')

    print(f"[NOTIFY] result -> telegram={sent_telegram}, email={sent_email}, method={notification_method}")


def can_send_message(item_id, ip_address):
    """Rate limiting - 1 pesan per scan per IP"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Check if IP already sent message for this item in last scan
    c.execute(
        'SELECT COUNT(*) FROM scan_tracking WHERE item_id = ? AND ip_address = ? AND action = ? AND timestamp > ?',
        (item_id, ip_address, 'message_sent', (datetime.now() - timedelta(hours=24)).isoformat())
    )
    count = c.fetchone()[0]
    conn.close()
    
    return count == 0


def log_message_sent(item_id, ip_address):
    """Log message untuk rate limiting"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO scan_tracking (item_id, ip_address, timestamp, action) VALUES (?, ?, ?, ?)',
        (item_id, ip_address, datetime.now().isoformat(), 'message_sent')
    )
    conn.commit()
    conn.close()
ADMIN_PIN = os.getenv('ADMIN_PIN', '9999')

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return render_template('admin_login.html')
    notify_status = request.args.get('notify_status', '')
    return render_template('admin.html', notify_status=notify_status)

@app.route('/admin_login', methods=['POST'])
def admin_login():
    pin_input = request.form.get('pin')
    if pin_input == ADMIN_PIN:
        session['is_admin'] = True
        return redirect(url_for('admin'))
    else:
        return "PIN Admin Salah! Akses Ditolak.", 403

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/generate_blank', methods=['POST'])
def generate_blank():
    if not session.get('is_admin'):
        return redirect(url_for('admin'))
        
    unique_id = str(uuid.uuid4())[:8] 
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO items (id, item_name, pin, finder_message, lat, lng) VALUES (?, "", "", "", "", "")', (unique_id,))
    conn.commit()
    conn.close()
    
    blank_link = f"{request.host_url}found/{unique_id}"
    return render_template('admin.html', blank_link=blank_link, tag_id=unique_id)


@app.route('/admin_create_tag', methods=['POST'])
def admin_create_tag():
    if not session.get('is_admin'):
        return redirect(url_for('admin'))

    item_name = request.form.get('item_name', '').strip()
    pin = request.form.get('pin', '').strip()
    owner_name = request.form.get('owner_name', '').strip()
    owner_whatsapp = request.form.get('owner_whatsapp', '').strip()
    owner_bio = request.form.get('owner_bio', '').strip()
    owner_avatar = request.form.get('owner_avatar', '').strip()
    owner_email = request.form.get('owner_email', '').strip()
    owner_telegram_id = request.form.get('owner_telegram_id', '').strip()
    notification_method = request.form.get('notification_method', 'email').strip()

    if not item_name or not pin or not owner_name or not owner_whatsapp or not owner_email:
        return "Data wajib belum lengkap (item, pin, nama, WA, email).", 400

    unique_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        '''INSERT INTO items (
            id, item_name, pin, owner_name, owner_whatsapp, owner_bio, owner_avatar,
            owner_email, owner_telegram_id, notification_method, finder_message,
            lat, lng, last_scan_timestamp, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', '', '', ?)''',
        (
            unique_id, item_name, pin, owner_name, owner_whatsapp, owner_bio, owner_avatar,
            owner_email, owner_telegram_id, notification_method, datetime.now().isoformat()
        )
    )
    conn.commit()
    conn.close()

    blank_link = f"{request.host_url}found/{unique_id}"
    return render_template('admin.html', blank_link=blank_link, tag_id=unique_id, created_ready=True)


@app.route('/admin_test_notify/<item_id>', methods=['POST'])
def admin_test_notify(item_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    conn.close()

    if not item:
        return redirect(url_for('admin', notify_status='Tag tidak ditemukan'))

    notify_owner(item)
    return redirect(url_for('admin', notify_status=f'Test notifikasi dipicu untuk tag {item_id}. Cek log terminal.'))


# ==========================================
# BAGIAN USER / PEMBELI / PENEMU
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activate', methods=['POST'])
def activate():
    if not session.get('is_admin'):
        return "Aktivasi hanya bisa dilakukan admin/penjual.", 403

    tag_id = request.form.get('tag_id').strip()
    item_name = request.form.get('item_name')
    pin = request.form.get('pin')
    owner_name = request.form.get('owner_name')
    owner_whatsapp = request.form.get('owner_whatsapp')
    owner_bio = request.form.get('owner_bio')
    owner_avatar = request.form.get('owner_avatar', '')
    owner_email = request.form.get('owner_email')
    owner_telegram_id = request.form.get('owner_telegram_id', '')
    notification_method = request.form.get('notification_method', 'email')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (tag_id,))
    item = c.fetchone()
    
    if not item:
        conn.close() 
        return "Tag ID tidak ditemukan di sistem kami. Cek kembali ID Anda.", 404
    if item[1] != "":
        conn.close()
        return "Tag ini sudah diaktivasi sebelumnya!", 403
        
    c.execute(
        '''UPDATE items SET item_name = ?, pin = ?, owner_name = ?, owner_whatsapp = ?, 
           owner_bio = ?, owner_avatar = ?, owner_email = ?, owner_telegram_id = ?, 
           notification_method = ?, created_at = ? WHERE id = ?''',
        (item_name, pin, owner_name, owner_whatsapp, owner_bio, owner_avatar, 
         owner_email, owner_telegram_id, notification_method, datetime.now().isoformat(), tag_id)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard', item_id=tag_id, pin=pin))

@app.route('/login', methods=['POST'])
def login():
    tag_id = request.form.get('tag_id').strip()
    pin = request.form.get('pin')
    return redirect(url_for('dashboard', item_id=tag_id, pin=pin))

@app.route('/found/<item_id>')
def found(item_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    
    if not item:
        conn.close()
        return "Tag NFC tidak valid/tidak terdaftar.", 404
        
    if item[1] == "":
        conn.close()
        return render_template('unclaimed.html', tag_id=item_id, platform_url=request.host_url)
    
    # Trigger notifikasi ke owner
    notify_owner(item)
    
    c.execute('SELECT sender, text, timestamp FROM messages WHERE item_id = ? ORDER BY id ASC', (item_id,))
    chat_history = c.fetchall()
    conn.close()
    
    # Cek apakah IP ini sudah bisa send message
    ip_address = request.remote_addr
    can_send = can_send_message(item_id, ip_address)
    
    return render_template('found.html', item_id=item_id, item=item, chat_history=chat_history, can_send=can_send)

@app.route('/dashboard')
def dashboard():
    item_id = request.args.get('item_id')
    provided_pin = request.args.get('pin')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    
    # PERBAIKAN: Tutup koneksi jika PIN salah
    if not item or item[2] != provided_pin:
        conn.close()
        return "Login Gagal. Tag ID atau PIN salah.", 403
        
    c.execute('SELECT sender, text FROM messages WHERE item_id = ? ORDER BY id ASC', (item_id,))
    chat_history = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', item=item, chat_history=chat_history, pin=provided_pin)

@app.route('/send_message/<item_id>', methods=['POST'])
def send_message(item_id):
    message = request.form.get('message')
    sender = request.form.get('sender')
    ip_address = request.remote_addr
    
    # Check rate limiting untuk penemu
    if sender == 'finder' and not can_send_message(item_id, ip_address):
        return "⚠️ Maaf, kamu hanya bisa mengirim satu pesan per scan. Tunggu scan berikutnya untuk kirim update.", 429
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO messages (item_id, sender, text, timestamp) VALUES (?, ?, ?, ?)', 
        (item_id, sender, message, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    # Log message untuk rate limiting
    if sender == 'finder':
        log_message_sent(item_id, ip_address)
    
    if sender == 'owner':
        pin = request.form.get('pin')
        return redirect(url_for('dashboard', item_id=item_id, pin=pin))
    else:
        return redirect(url_for('found', item_id=item_id))

@app.route('/update_location/<item_id>', methods=['POST'])
def update_location(item_id):
    data = request.get_json()
    lat = str(data.get('lat'))
    lng = str(data.get('lng'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE items SET lat = ?, lng = ?, last_scan_timestamp = ? WHERE id = ?', 
              (lat, lng, datetime.now().isoformat(), item_id))
    
    # Get item data to notify owner with location
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    conn.commit()
    conn.close()
    
    if item:
        # Send notification dengan koordinat
        notify_owner(item, coords_lat=lat, coords_lng=lng)
    
    return jsonify({"status": "success", "message": "Lokasi berhasil dikirim ke pemilik"})


@app.route('/Logo.svg')
def logo_asset():
    return send_from_directory('.', 'Logo.svg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)