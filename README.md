# Ketemuin

Ketemuin adalah aplikasi lost-and-found berbasis NFC dengan arsitektur static + serverless.

## Arsitektur

- Frontend: `index.html` (SPA)
- Database & Auth: Supabase
- Serverless notification: `netlify/functions/notify.js`
- Hosting: Netlify

## Fitur Utama

- Landing page produk yang responsif
- Admin login via Supabase Auth
- Dashboard admin untuk membuat profil owner
- Halaman publik owner: `/profile/{short_id}`
- Finder bisa kirim pesan dan share lokasi
- Notifikasi otomatis ke channel owner (email/Telegram/WhatsApp link fallback)
- Mini game tap/tangkap kucing di landing dan profile

## Setup Lokal

1. Buat project Supabase.
2. Jalankan `supabase-schema.sql` di SQL Editor Supabase.
3. Buat user admin di menu Auth > Users.
4. Copy `supabase-config.example.js` menjadi `supabase-config.js`.
5. Isi `supabase-config.js`:

```javascript
window.KETEMUIN_SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co";
window.KETEMUIN_SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";
```

6. Jalankan lokal (opsional, untuk test fungsi Netlify):

```bash
npm install
npx netlify dev
```

## Deploy Netlify

1. Push repo ke GitHub.
2. Import project di Netlify.
3. Set environment variables `KETEMUIN_SUPABASE_URL` dan `KETEMUIN_SUPABASE_ANON_KEY` di Netlify.
4. Build command dijalankan otomatis lewat `netlify.toml` untuk generate `supabase-config.js`.
5. Publish directory: root project.
6. Pastikan `netlify.toml` dan folder `netlify/functions` terbaca.

## Environment Variable Netlify

Set di Site Settings > Environment Variables:

- `EMAIL_SENDER`
- `EMAIL_PASSWORD`
- `SMTP_SERVER`
- `SMTP_PORT`
- `TELEGRAM_BOT_TOKEN`

## Struktur File Inti

- `index.html`
- `netlify.toml`
- `netlify/functions/notify.js`
- `supabase-schema.sql`
- `supabase-config.example.js`
- `package.json`

## Catatan

- Jangan commit `supabase-config.js` dan `.env`.
- Walau tidak di-commit, `supabase-config.js` tetap harus dibuat saat build deploy. Di project ini file tersebut digenerate otomatis dari environment variables.
- Anon key Supabase boleh dipakai frontend, tapi RLS wajib aktif.

