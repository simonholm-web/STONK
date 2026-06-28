# StonkTrack

Daily robotics & AI stock mention poller. Fetches real data from Adanos (Reddit + News sentiment), compares current 30 days vs previous 30 days, and produces a buy rating (1–100) for every ticker.

**Strong buy = Buzz ≥30 AND Köprek ≥30 AND bullish news gate passes.**

---

## Setup (5 minutes)

### 1 — Create a GitHub repo

Go to github.com → New repository → name it `stonktrack` → Public → Create.

### 2 — Upload these files

Upload all files from this zip to the root of your repo:
- `poll.py`
- `dashboard.html`
- `.github/workflows/daily_poll.yml`

### 3 — Add your Adanos API key as a secret

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

- Name: `ADANOS_KEY`
- Value: your Adanos key (the new rotated one)

### 4 — Run the workflow manually (first time)

Go to **Actions → Daily StonkTrack Poll → Run workflow**.

This runs `poll.py`, fetches all tickers from Adanos, and saves `data/results.json` to your repo. Takes about 3–5 minutes.

After it finishes you will see `data/results.json` appear in your repo.

### 5 — Open the dashboard

Open `dashboard.html` in your browser (just double-click it locally, or host it on GitHub Pages).

When it asks for the GitHub raw URL, enter:
```
https://raw.githubusercontent.com/YOUR_USERNAME/stonktrack/main/data/results.json
```

Replace `YOUR_USERNAME` with your actual GitHub username.

The dashboard reads that JSON file and shows you the full ranked list.

---

## Schedule

The workflow runs automatically every weekday at **07:00 Stockholm time** (05:00 UTC). You can also trigger it manually any time from the Actions tab.

## Costs

- GitHub Actions: **free** (2,000 minutes/month on free plan, this uses ~5 minutes/day)
- Adanos: **250 calls/month free** — scanning 52 tickers uses 3 calls each = 156 calls per run. That fits the free tier for ~1 run per month. For daily runs, upgrade to the Hobby plan (~$29/mo or check current pricing at adanos.org).

## Adding more tickers

Edit the `TICKERS` list in `poll.py` and push. The workflow picks up the change automatically.
