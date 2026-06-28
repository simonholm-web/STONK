"""
StonkTrack daily poller
Fetches Adanos Reddit + News sentiment for all tickers
Compares current 30 days vs previous 30 days
Saves results to data/results.json for the dashboard to read
"""

import json
import os
import time
import requests
from datetime import datetime, timezone, timedelta

ADANOS_KEY = os.environ["ADANOS_KEY"]

HEADERS = {
    "X-API-Key": ADANOS_KEY,
    "Accept": "application/json",
}

TICKERS = [
    # US NASDAQ
    {"s": "RCAT",  "n": "Red Cat Holdings",        "c": "drone",      "ex": "us"},
    {"s": "ONDS",  "n": "Ondas Holdings",           "c": "drone",      "ex": "us"},
    {"s": "ACHR",  "n": "Archer Aviation",          "c": "drone",      "ex": "us"},
    {"s": "JOBY",  "n": "Joby Aviation",            "c": "drone",      "ex": "us"},
    {"s": "KTOS",  "n": "Kratos Defense",           "c": "drone",      "ex": "us"},
    {"s": "AVAV",  "n": "AeroVironment",            "c": "drone",      "ex": "us"},
    {"s": "MNTS",  "n": "Momentus",                 "c": "drone",      "ex": "us"},
    {"s": "RKLB",  "n": "Rocket Lab",               "c": "space",      "ex": "us"},
    {"s": "ASTS",  "n": "AST SpaceMobile",          "c": "space",      "ex": "us"},
    {"s": "LUNR",  "n": "Intuitive Machines",       "c": "space",      "ex": "us"},
    {"s": "IONQ",  "n": "IonQ",                     "c": "quantum",    "ex": "us"},
    {"s": "QBTS",  "n": "D-Wave Quantum",           "c": "quantum",    "ex": "us"},
    {"s": "RGTI",  "n": "Rigetti Computing",        "c": "quantum",    "ex": "us"},
    {"s": "QUBT",  "n": "Quantum Computing Inc",    "c": "quantum",    "ex": "us"},
    {"s": "CBRS",  "n": "Cerebras Systems",         "c": "chips",      "ex": "us"},
    {"s": "POET",  "n": "POET Technologies",        "c": "chips",      "ex": "us"},
    {"s": "KOPN",  "n": "Kopin Corporation",        "c": "chips",      "ex": "us"},
    {"s": "INDI",  "n": "indie Semiconductor",      "c": "chips",      "ex": "us"},
    {"s": "AEVA",  "n": "Aeva Technologies",        "c": "autonomous", "ex": "us"},
    {"s": "LAZR",  "n": "Luminar Technologies",     "c": "autonomous", "ex": "us"},
    {"s": "AUR",   "n": "Aurora Innovation",        "c": "autonomous", "ex": "us"},
    {"s": "OUST",  "n": "Ouster Lidar",             "c": "autonomous", "ex": "us"},
    {"s": "MVIS",  "n": "MicroVision",              "c": "autonomous", "ex": "us"},
    {"s": "ARBE",  "n": "Arbe Robotics",            "c": "autonomous", "ex": "us"},
    {"s": "SERV",  "n": "Serve Robotics",           "c": "humanoid",   "ex": "us"},
    {"s": "RR",    "n": "Richtech Robotics",        "c": "humanoid",   "ex": "us"},
    {"s": "KSCP",  "n": "Knightscope",              "c": "humanoid",   "ex": "us"},
    {"s": "BBAI",  "n": "BigBear.ai",               "c": "ai",         "ex": "us"},
    {"s": "SOUN",  "n": "SoundHound AI",            "c": "ai",         "ex": "us"},
    {"s": "KULR",  "n": "KULR Technology",          "c": "ai",         "ex": "us"},
    {"s": "UPST",  "n": "Upstart Holdings",         "c": "ai",         "ex": "us"},
    {"s": "NET",   "n": "Cloudflare",               "c": "ai",         "ex": "us"},
    {"s": "CRWD",  "n": "CrowdStrike",              "c": "ai",         "ex": "us"},
    {"s": "AI",    "n": "C3.ai",                    "c": "ai",         "ex": "us"},
    {"s": "MNDY",  "n": "Monday.com",               "c": "ai",         "ex": "us"},
    # Nasdaq Stockholm
    {"s": "HEXA-B","n": "Hexagon AB",               "c": "autonomous", "ex": "se"},
    {"s": "MYCR",  "n": "Mycronic AB",              "c": "chips",      "ex": "se"},
    {"s": "SAAB-B","n": "Saab AB",                  "c": "drone",      "ex": "se"},
    {"s": "TOBII", "n": "Tobii AB",                 "c": "autonomous", "ex": "se"},
    {"s": "SIVERS","n": "Sivers Semiconductors",    "c": "chips",      "ex": "se"},
    {"s": "SINCH", "n": "Sinch AB",                 "c": "ai",         "ex": "se"},
    {"s": "EVO",   "n": "Evolution AB",             "c": "ai",         "ex": "se"},
    {"s": "ATCO-A","n": "Atlas Copco A",            "c": "humanoid",   "ex": "se"},
    {"s": "HUSQ-B","n": "Husqvarna B",              "c": "humanoid",   "ex": "se"},
    {"s": "VITEC", "n": "Vitec Software",           "c": "ai",         "ex": "se"},
    {"s": "NCAB",  "n": "NCAB Group",               "c": "chips",      "ex": "se"},
    {"s": "NIBE-B","n": "NIBE Industrier B",        "c": "autonomous", "ex": "se"},
    {"s": "BURE",  "n": "Bure Equity AB",           "c": "ai",         "ex": "se"},
    # First North
    {"s": "EKOBOT","n": "Ekobot AB",                "c": "humanoid",   "ex": "fn"},
    {"s": "CELLINK","n":"CELLINK AB",               "c": "humanoid",   "ex": "fn"},
    {"s": "IMINT", "n": "IMINT Image Intelligence", "c": "ai",         "ex": "fn"},
    {"s": "NEONODE","n":"Neonode Inc",              "c": "autonomous", "ex": "fn"},
    {"s": "CLAVISTER","n":"Clavister Holding",      "c": "ai",         "ex": "fn"},
]

def adanos_get(path, params=None):
    url = f"https://api.adanos.org{path}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if r.status_code == 429:
        print(f"  Rate limited on {path}, waiting 10s...")
        time.sleep(10)
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    return r

def fetch_ticker(sym):
    today = datetime.now(timezone.utc).date()
    # Current 30 days
    from_curr = (today - timedelta(days=30)).isoformat()
    to_curr   = today.isoformat()
    # Previous 30 days (30-60 days ago)
    from_prev = (today - timedelta(days=60)).isoformat()
    to_prev   = (today - timedelta(days=30)).isoformat()

    reddit_curr = adanos_get(f"/reddit/stocks/v1/stock/{sym}", {"from": from_curr, "to": to_curr})
    time.sleep(0.4)
    reddit_prev = adanos_get(f"/reddit/stocks/v1/stock/{sym}", {"from": from_prev, "to": to_prev})
    time.sleep(0.4)
    news_curr = adanos_get(f"/news/stocks/v1/stock/{sym}", {"from": from_curr, "to": to_curr})
    time.sleep(0.4)

    result = {}

    if reddit_curr.ok:
        rd = reddit_curr.json()
        result["reddit_mentions"]   = rd.get("mentions") or rd.get("total_mentions") or 0
        result["bullish_pct"]       = rd.get("bullish_pct") or rd.get("positive_pct") or 0
        result["bearish_pct"]       = rd.get("bearish_pct") or rd.get("negative_pct") or 0
        result["buzz_score"]        = rd.get("buzz_score") or 0
        result["trend"]             = rd.get("trend") or "stable"
        result["upvotes"]           = rd.get("upvotes") or rd.get("total_upvotes") or 0
        result["unique_authors"]    = rd.get("unique_authors") or 0
    else:
        print(f"  Reddit current failed: {reddit_curr.status_code} — {reddit_curr.text[:100]}")
        result["reddit_mentions"] = 0
        result["bullish_pct"] = 0
        result["bearish_pct"] = 0
        result["buzz_score"] = 0
        result["trend"] = "stable"

    if reddit_prev.ok:
        rp = reddit_prev.json()
        result["reddit_prev_mentions"] = rp.get("mentions") or rp.get("total_mentions") or 0
    else:
        result["reddit_prev_mentions"] = 0

    if news_curr.ok:
        nd = news_curr.json()
        result["news_mentions"]   = nd.get("mentions") or nd.get("total_mentions") or 0
        result["news_bullish_pct"] = nd.get("bullish_pct") or nd.get("positive_pct") or 0
        result["news_trend"]      = nd.get("trend") or "stable"
        result["news_buzz"]       = nd.get("buzz_score") or 0
    else:
        result["news_mentions"] = 0
        result["news_bullish_pct"] = 0
        result["news_trend"] = "stable"
        result["news_buzz"] = 0

    return result

def calc_scores(data):
    curr_m   = data.get("reddit_mentions", 0)
    prev_m   = data.get("reddit_prev_mentions", 0)
    bull_pct = data.get("bullish_pct", 0)
    trend    = data.get("trend", "stable")
    buzz_raw = data.get("buzz_score", 0)
    news_m   = data.get("news_mentions", 0)
    news_bul = data.get("news_bullish_pct", 0)
    news_tr  = data.get("news_trend", "stable")

    # Mention spike vs last month
    if prev_m > 0:
        spike = ((curr_m - prev_m) / prev_m) * 100
    elif curr_m > 0:
        spike = 300.0
    else:
        spike = 0.0

    # --- BUZZ (0-50): only count if majority bullish ---
    buzz = 0
    if bull_pct >= 40:
        if   spike >= 300 and prev_m <= 30: buzz += 22
        elif spike >= 200:                  buzz += 18
        elif spike >= 100:                  buzz += 13
        elif spike >= 50:                   buzz += 8
        elif spike >= 20:                   buzz += 4

        if   bull_pct >= 70: buzz += 14
        elif bull_pct >= 55: buzz += 9
        elif bull_pct >= 45: buzz += 5

        if   trend == "rising":  buzz += 10
        elif trend == "stable":  buzz += 2
        elif trend == "falling": buzz -= 4

        if   buzz_raw >= 70: buzz += 4
        elif buzz_raw >= 50: buzz += 2

    buzz = max(0, min(50, round(buzz)))

    # --- KOPREK (0-50): news + momentum ---
    koprek = 0
    good_news = news_m > 0 and news_bul > 45

    if good_news:
        if   news_bul >= 70: koprek += 22
        elif news_bul >= 55: koprek += 15
        else:                koprek += 10
        if   news_tr == "rising": koprek += 12
        elif news_tr == "stable": koprek += 5

    if spike >= 200 and bull_pct >= 50: koprek += 12
    elif spike >= 100 and bull_pct >= 50: koprek += 8
    elif spike >= 50  and bull_pct >= 45: koprek += 4

    koprek = max(0, min(50, round(koprek)))

    total     = buzz + koprek
    is_strong = buzz >= 30 and koprek >= 30 and good_news and total >= 75
    is_watch  = not is_strong and total >= 55

    return {
        "buzz":        buzz,
        "koprek":      koprek,
        "total":       total,
        "is_strong":   is_strong,
        "is_watch":    is_watch,
        "good_news":   good_news,
        "mention_spike": round(spike),
    }

def main():
    print(f"StonkTrack poll starting at {datetime.now(timezone.utc).isoformat()}")
    all_results = []

    for i, t in enumerate(TICKERS):
        sym = t["s"]
        print(f"[{i+1}/{len(TICKERS)}] Fetching {sym}...")
        try:
            raw = fetch_ticker(sym)
            scores = calc_scores(raw)
            row = {**t, **raw, **scores, "fetched_at": datetime.now(timezone.utc).isoformat()}
            all_results.append(row)
            print(f"  total={scores['total']} buzz={scores['buzz']} kr={scores['koprek']} "
                  f"spike={scores['mention_spike']}% bull={raw.get('bullish_pct',0)}% "
                  f"strong={scores['is_strong']}")
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results.append({**t, "error": str(e), "total": 0, "buzz": 0,
                                 "koprek": 0, "is_strong": False, "is_watch": False,
                                 "fetched_at": datetime.now(timezone.utc).isoformat()})

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ticker_count": len(all_results),
        "strong_buys":  sum(1 for r in all_results if r.get("is_strong")),
        "results":      all_results,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. {output['strong_buys']} strong buys out of {len(all_results)} tickers.")
    print("Saved to data/results.json")

if __name__ == "__main__":
    main()
