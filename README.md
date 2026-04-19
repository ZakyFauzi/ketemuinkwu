# Ketemuin Free Cloud Edition

Ketemuin sekarang berjalan tanpa Flask dan tanpa server pribadi.

Arsitektur baru:
- Frontend: static single page di index.html
- Database/Auth: Supabase free tier
- Hosting: Netlify atau Vercel free tier

## Yang kamu dapat

- Landing page public
- Admin login pakai Supabase Auth
- Admin dashboard untuk membuat owner profile
- Public profile per owner di route /profile/{short_id}
- Finder bisa:
  - kirim pesan (tersimpan ke database)
  - share lokasi (tersimpan ke database)
  - buka channel WhatsApp/Email/Telegram

## Setup sekali saja

1. Buat project baru di Supabase
2. Buka SQL Editor, jalankan file supabase-schema.sql
3. Buat user admin di Auth -> Users (email + password)
4. Copy file supabase-config.example.js menjadi supabase-config.js
5. Isi URL dan ANON KEY Supabase di supabase-config.js

Contoh isi supabase-config.js:

window.KETEMUIN_SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co";
window.KETEMUIN_SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";

## Deploy gratis

Netlify:
- Import repo
- Tidak perlu build command
- Publish root
- netlify.toml sudah menyiapkan SPA rewrite

Vercel:
- Import repo
- Framework: Other
- Tidak perlu build command
- vercel.json sudah menyiapkan rewrite

## Catatan penting

- File supabase-config.js jangan di-commit
- .gitignore sudah mengecualikan supabase-config.js
- .env dan app.py sekarang tidak dipakai untuk arsitektur ini

## Struktur file penting

- index.html
- netlify.toml
- vercel.json
- supabase-schema.sql
- supabase-config.example.js

