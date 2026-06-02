# 42 Tracker - Auth Server (Deploy to Vercel)

## Deploy steps

### 1. Push to GitHub
Create a new repo and push the contents of this folder.

### 2. Create a Vercel account
Go to [https://vercel.com](https://vercel.com) and sign up (free tier is fine).

### 3. Import your project
- Click **Add New → Project**
- Connect your GitHub repo
- Vercel will auto-detect the Python app via `vercel.json` — no extra settings needed
- Click **Deploy**

### 4. Set environment variables
In Vercel dashboard → your project → **Settings → Environment Variables**, add:

| Key | Value |
|-----|-------|
| `CLIENT_ID` | your 42 app's client UID |
| `CLIENT_SECRET` | your 42 app's client secret |
| `REDIRECT_URI` | `https://YOUR-PROJECT-NAME.vercel.app/callback` |

After adding them, go to **Deployments** and click **Redeploy** so the vars take effect.

### 5. Update your 42 app's redirect URI
Go to [https://profile.intra.42.fr/oauth/applications](https://profile.intra.42.fr/oauth/applications)
→ your app → add this redirect URI:
```
https://YOUR-PROJECT-NAME.vercel.app/callback
```

### 6. Update the local script
In `42-tracker-local/tracker.py`, change this line:
```python
AUTH_SITE = "https://YOUR-APP-URL.onrender.com"
```
to your actual Vercel URL:
```python
AUTH_SITE = "https://YOUR-PROJECT-NAME.vercel.app"
```

---

## How users use it

1. Visit your Vercel URL
2. Click **Login with 42 Intra**
3. Copy the token shown
4. Run `./launch.sh <peer> <logged|delogged>` and paste the token

Token lasts **2 hours**. After that, they visit the site again to get a new one.

---

## What changed from the Render version

| | Render | Vercel |
|---|---|---|
| Runtime | `gunicorn app:app` | `@vercel/python` (auto) |
| Config file | none needed | `vercel.json` |
| `requirements.txt` | includes `gunicorn` | `gunicorn` removed |
| `app.py` | has `if __name__ == "__main__"` block | removed (not needed) |
| Cold starts | ~30–50s after inactivity | ~1–3s |
