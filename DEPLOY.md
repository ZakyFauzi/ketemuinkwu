# Deploy Guide - Ketemuin Free Cloud

## Arsitektur final

- Frontend static: index.html
- Data cloud: Supabase (free)
- Hosting: Netlify atau Vercel (free)
- Tanpa Flask, tanpa Render

## 1) Setup Supabase

1. Buat project baru di https://supabase.com
2. Masuk SQL Editor
3. Jalankan isi file supabase-schema.sql
4. Masuk Auth -> Users -> Add user
   - isi email admin
   - isi password admin

## 2) Setup config frontend

1. Copy supabase-config.example.js jadi supabase-config.js
2. Isi nilai berikut:

window.KETEMUIN_SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co";
window.KETEMUIN_SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";

Ambil nilai dari Supabase:
- Project Settings -> API -> Project URL
- Project Settings -> API -> anon public key

## 3) Deploy ke Netlify

1. Push project ke GitHub
2. Masuk Netlify -> Add new site -> Import from GitHub
3. Build command kosong
4. Publish directory kosong/root
5. Deploy

netlify.toml sudah handle rewrite route /admin dan /profile/* ke index.html.

## 4) Deploy ke Vercel

1. Import project dari GitHub
2. Framework preset: Other
3. Build command kosong
4. Output directory kosong
5. Deploy

vercel.json sudah handle rewrite semua route ke index.html.

## 5) Cek flow

- / -> landing
- /admin -> login admin
- /admin (setelah login) -> dashboard owner
- /profile/{short_id} -> profile publik

## Catatan keamanan

- Jangan commit supabase-config.js jika berisi key produksi
- Walau anon key public, RLS policy tetap wajib aktif
- Jangan pakai service_role key di frontend

