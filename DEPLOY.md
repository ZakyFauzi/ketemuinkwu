# Deployment Guide - Ketemuin Static App

## Quickstart (2 Minutes)

### Step 1: Prepare Files
You need:
- `index.html` ✅ (done)
- `netlify.toml` ✅ (done)

That's it! No build process, no dependencies, nothing else needed.

### Step 2: Deploy

#### **Option A: Netlify (Recommended)**

**Method 1 - Drag & Drop (Easiest)**
```
1. Go to: https://app.netlify.com/drop
2. Drag the "ketemuin-development" folder
3. Wait 30 seconds...
4. Your site is live! 🎉
```

**Method 2 - Git (Auto-deploy on push)**
```
1. Push code to GitHub
2. Go to: https://app.netlify.com
3. Click "New site from Git"
4. Select your GitHub repo
5. Click "Deploy site"
6. Every push = auto-deploy
```

#### **Option B: Vercel**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd ketemuin-development
vercel

# Select your project name
# Click deploy
# Done!
```

#### **Option C: GitHub Pages (Free Tier)**

```bash
# Push to GitHub
git push origin main

# Go to: Settings → Pages
# Select "Deploy from a branch"
# Choose: main branch
# Your site: https://USERNAME.github.io/ketemuin-development
```

---

## Verify Deployment Works

After deploy, check:

1. **Homepage loads**
   - Should see "Ketemuin" header with tabs
   
2. **Setup Owner form works**
   - Fill form → click Save
   - Should show green success message

3. **Link generates**
   - Copy link from "Profil Saya" tab
   - Should contain `?owner=ID`

4. **Mobile responsive**
   - Open on phone browser
   - Should be full-width, readable

5. **Geolocation works**
   - Go to "Import/Use" tab
   - Click "Bagikan Lokasi"
   - Browser asks permission → allow
   - Should show "Location shared" message

---

## Custom Domain (Optional)

### Netlify
```
1. Settings → Domain settings
2. Click "Add custom domain"
3. Add your domain (ketemuin.id, etc)
4. Follow DNS instructions
```

### Vercel
```
1. Settings → Domains
2. Add your domain
3. Update DNS records
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Blank page | Clear browser cache (Ctrl+Shift+Del) |
| localStorage shows old data | Hard refresh (Ctrl+F5 or Shift+F5) |
| Link doesn't work | Check URL has `?owner=ID` part |
| Geolocation error | Browser needs HTTPS (auto on Netlify/Vercel) |
| WhatsApp link broken | Check phone format: 628XXXXXXXXX |

---

## File Checklist Before Deploy

```
ketemuin-development/
├── index.html ✅ (Must have)
├── netlify.toml ✅ (For Netlify only, optional for Vercel)
├── README.md (Reference only)
├── .env (Not used anymore, can ignore)
└── app.py (Archive - not needed)
```

Only need: `index.html` + `netlify.toml`

---

## After Deployment

### Share with Users

1. **Create QR Code**
   - Copy your deployment link
   - Go to: https://qr-code-generator.com
   - Paste link → Generate QR
   - Download PNG

2. **Print & Distribute**
   - Print QR stickers
   - Attach to keychains/bags/valuables
   - Anyone who finds it: scan → instant contact

3. **Monitor**
   - Open your link
   - Check "Profil Saya" tab
   - See who scanned your code (via localStorage on your device)

---

## Updates & Changes

Want to modify the app later?

### If using Netlify + Git:
```bash
# Edit index.html
# Push to GitHub
git add index.html
git commit -m "Update features"
git push

# Netlify auto-deploys in ~1 minute ✅
```

### If using Drag-Drop:
```bash
# Edit index.html locally
# Go to Netlify → Deploys → Drag new folder again
# Old version replaced automatically
```

---

## Scale Up (Future)

Current setup handles:
- ✅ Unlimited users
- ✅ Unlimited profiles  
- ✅ Global CDN (fast worldwide)
- ✅ No maintenance needed

If you add backend later (notifications, multi-device sync, analytics), you'll need:
- Serverless function (Netlify Functions / Vercel Functions)
- Or separate backend (but static frontend stays free)

---

**Ready to deploy?** Pick Option A/B/C above and you're live in minutes! 🚀
