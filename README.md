# 42 Tracker - Auth Server (Deploy to Render)

## Deploy steps

### 1. Push to GitHub
Create a new repo and push the contents of this folder (`42-tracker-web/`).

### 2. Create a Render account
Go to [https://render.com](https://render.com) and sign up (free tier is fine).

### 3. Create a new Web Service
- Click **New → Web Service**
- Connect your GitHub repo
- Settings:
  - **Runtime:** Python
  - **Build command:** `pip install -r requirements.txt`
  - **Start command:** `gunicorn app:app`
  - **Instance type:** Free

### 4. Set environment variables
In Render dashboard → your service → **Environment**, add:

| Key | Value |
|-----|-------|
| `CLIENT_ID` | your 42 app's client UID |
| `CLIENT_SECRET` | your 42 app's client secret |
| `REDIRECT_URI` | `https://YOUR-SERVICE-NAME.onrender.com/callback` |

### 5. Update your 42 app's redirect URI
Go to [https://profile.intra.42.fr/oauth/applications](https://profile.intra.42.fr/oauth/applications)
→ your app → add this redirect URI:
```
https://YOUR-SERVICE-NAME.onrender.com/callback
```

### 6. Update the local script
In `42-tracker-local/tracker.py`, change this line:
```python
AUTH_SITE = "https://YOUR-APP-URL.onrender.com"
```
to your actual Render URL.

---

## How users use it

1. Visit your Render URL
2. Click **Login with 42 Intra**
3. Copy the token shown
4. Run `./launch.sh <peer> <logged|delogged>` and paste the token

Token lasts **2 hours**. After that, they visit the site again to get a new one.
