# Vercel ile Yayınlama

Frontend Vercel'de çalışır; **backend ayrıca yayında olmalı**. Aksi halde giriş ve veri çalışmaz.

---

## 404 NOT_FOUND alıyorsanız

Bu repo **monorepo**; uygulama **`frontend`** klasöründe. Vercel’in projeyi doğru build edebilmesi için:

1. **https://vercel.com** → Projenize girin (otomat-ihale).
2. **Settings** → **General**.
3. **Root Directory** satırında **Edit** deyin.
4. **`frontend`** yazın veya seçin → **Save**.
5. **Deployments** → son deployment’ta **⋯** → **Redeploy**.

Bundan sonra https://otomat-ihale.vercel.app tekrar açılmalı.

---

## 1. Vercel proje ayarları

- **Root Directory:** `frontend` (monorepo — **mutlaka** ayarlayın, yoksa 404 alırsınız)
- **Build Command:** `npm run build` (varsayılan)
- **Output Directory:** `.next` (Next.js varsayılan)

## 2. Ortam değişkeni (zorunlu)

Backend'i bir yerde yayınlayın (Railway, Render, Fly.io, vb.) ve API adresini ekleyin:

| Ad | Değer |
|----|--------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://SIZIN-BACKEND-ADRESINIZ/api/v1` |

Örnek: Backend `https://otomat-ihale-api.railway.app` ise:
- `NEXT_PUBLIC_API_BASE_URL` = `https://otomat-ihale-api.railway.app/api/v1`

Bu değişkeni Vercel projesinde **Settings → Environment Variables** bölümünden ekleyin, sonra **Redeploy** yapın.

## 3. Backend nereye deploy edilir?

- **Railway:** https://railway.app — GitHub bağla, `backend/` veya Docker ile deploy
- **Render:** https://render.com — Web Service, Python/FastAPI
- **Fly.io:** https://fly.io — `fly launch` ile

Backend'de PostgreSQL veya SQLite kullanıyorsanız, Railway/Render üzerinde veritabanı ekleyip `DATABASE_URL` ile bağlayın.
