from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_kewirausahaan_2026'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            item_name TEXT,
            pin TEXT,
            finder_message TEXT,
            lat TEXT,
            lng TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            sender TEXT,
            text TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# BAGIAN ADMIN
# ==========================================
ADMIN_PIN = "9999"

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return render_template('admin_login.html')
    return render_template('admin.html')

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


# ==========================================
# BAGIAN USER / PEMBELI / PENEMU
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activate', methods=['POST'])
def activate():
    tag_id = request.form.get('tag_id').strip()
    item_name = request.form.get('item_name')
    pin = request.form.get('pin')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (tag_id,))
    item = c.fetchone()
    
    # PERBAIKAN: Tutup koneksi sebelum mengembalikan pesan error
    if not item:
        conn.close() 
        return "Tag ID tidak ditemukan di sistem kami. Cek kembali ID Anda.", 404
    if item[1] != "":
        conn.close()
        return "Tag ini sudah diaktivasi sebelumnya!", 403
        
    c.execute('UPDATE items SET item_name = ?, pin = ? WHERE id = ?', (item_name, pin, tag_id))
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
    
    # PERBAIKAN: Tutup koneksi sebelum merender halaman unclaimed atau error
    if not item:
        conn.close()
        return "Tag NFC tidak valid/tidak terdaftar.", 404
        
    if item[1] == "":
        conn.close()
        return render_template('unclaimed.html', tag_id=item_id, platform_url=request.host_url)
    
    c.execute('SELECT sender, text FROM messages WHERE item_id = ? ORDER BY id ASC', (item_id,))
    chat_history = c.fetchall()
    conn.close()
    
    return render_template('found.html', item_id=item_id, item_name=item[1], chat_history=chat_history)

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
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (item_id, sender, text) VALUES (?, ?, ?)', (item_id, sender, message))
    conn.commit()
    conn.close()
    
    if sender == 'owner':
        pin = request.form.get('pin')
        return redirect(url_for('dashboard', item_id=item_id, pin=pin))
    else:
        return redirect(url_for('found', item_id=item_id))

@app.route('/update_location/<item_id>', methods=['POST'])
def update_location(item_id):
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE items SET lat = ?, lng = ? WHERE id = ?', (str(data.get('lat')), str(data.get('lng')), item_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)