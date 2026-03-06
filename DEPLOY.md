# Tek Tık Deploy — Backend + Vercel Frontend

## 1. Backend’i Render’da yayına alın (ücretsiz)

1. **https://dashboard.render.com** → Giriş (GitHub ile).
2. **New +** → **Blueprint**.
3. **Connect a repository** → `GorkemMergenay/Otomat_ihale` seçin.
4. Render `render.yaml` dosyasını görür; **Apply** deyin.
5. Oluşan servisler:
   - **otomat-ihale-db** (PostgreSQL, ücretsiz)
   - **otomat-ihale-api** (Backend API)
6. **otomat-ihale-api** → **Settings** → **Environment** bölümünde `DATABASE_URL` otomatik gelir.
7. Deploy bitince **otomat-ihale-api** için verilen URL’i kopyalayın (örn. `https://otomat-ihale-api.onrender.com`).

**Seed (ilk kurulum):** Giriş yapabilmek için bir kere seed gerekir.

- **Render Shell:** otomat-ihale-api → **Shell** → `python /app/scripts/seed_data.py` (ortam zaten hazır).
- **Yerelden:** Render Dashboard → otomat-ihale-db → **Info** → **Internal Database URL** kopyalayın. Yerelde:
  ```bash
  cd "/Users/gorkemmergenay/Documents/New project 2"
  DATABASE_URL="postgresql://..." PYTHONPATH=backend:. python scripts/seed_data.py
  ```
  Sonra Vercel’de giriş: `admin@otomat.local` / `Otomat123!`

---

## 2. Vercel’de API adresini ayarlayın

1. **https://vercel.com** → Projeniz (otomat-ihale) → **Settings** → **Environment Variables**.
2. Ekle:
   - **Name:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** `https://SIZIN-RENDER-API-URL/api/v1`  
     Örnek: `https://otomat-ihale-api.onrender.com/api/v1`
3. **Save** → **Deployments** → son deployment’ta **⋯** → **Redeploy**.

Birkaç dakika sonra **https://otomat-ihale.vercel.app** giriş ve veri ile çalışır.

---

## 3. (İsteğe bağlı) Railway ile backend

1. **https://railway.app** → **Start a New Project** → **Deploy from GitHub repo** → `GorkemMergenay/Otomat_ihale`.
2. Root’taki **Dockerfile** otomatik kullanılır.
3. **Variables** kısmında `DATABASE_URL` ekleyin: Railway’de **New** → **Database** → **PostgreSQL** ekleyip otomatik oluşan `DATABASE_URL`’i kopyalayın.
4. Servis URL’i (örn. `https://xxx.railway.app`) → Vercel’de `NEXT_PUBLIC_API_BASE_URL` = `https://xxx.railway.app/api/v1` yapın ve Redeploy.

---

## Özet

| Adım | Nerede | Ne yapılır |
|------|--------|------------|
| 1 | Render | Blueprint ile backend + DB deploy, API URL’i kopyala |
| 2 | Vercel | `NEXT_PUBLIC_API_BASE_URL` = `https://.../api/v1`, Redeploy |
| 3 | (Opsiyonel) | Seed: Render Shell veya yerelde `seed_data.py` |

Bu adımlardan sonra **https://otomat-ihale.vercel.app** tam çalışır.
