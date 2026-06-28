from flask import Flask, redirect, Response, request
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)

# ----------------------------
# 📺 KANÁLY
# ----------------------------
CHANNELS = {
    "oneplay1": ["ONEPLAY SPORT 1", "https://strumyk.cfd/e/gitshop/oneplaysport1.php"],
    "oneplay2": ["ONEPLAY SPORT 2", "https://strumyk.cfd/e/gitshop/oneplaysport2.php"],
    "oneplay3": ["ONEPLAY SPORT 3", "https://strumyk.cfd/e/gitshop/oneplaysport3.php"],
    "oneplay4": ["ONEPLAY SPORT 4", "https://strumyk.cfd/e/gitshop/oneplaysport4.php"],

    "nova1": ["NOVA SPORT 1", "https://sites.google.com/view/jablecnatasticka23/kanaly/ns1"],
    "nova2": ["NOVA SPORT 2", "https://sites.google.com/view/jablecnatasticka23/kanaly/ns2"],
    "nova3": ["NOVA SPORT 3", "https://sites.google.com/view/jablecnatasticka23/kanaly/ns3"],
    "nova4": ["NOVA SPORT 4", "https://sites.google.com/view/jablecnatasticka23/kanaly/ns4"],
    "nova5": ["NOVA SPORT 5", "https://sites.google.com/view/jablecnatasticka23/kanaly/ns5"],
    "nova6": ["NOVA SPORT 6", "https://sites.google.com/view/jablecnatasticka23/kanaly/ns6"],

    "ctsport": ["CT SPORT", "https://dlstreams.top/stream/stream-1033.php"],

    "sport1": ["SPORT 1", "https://abcsport.top/sport1cz.php"],
    "sport2": ["SPORT 2", "https://abcsport.top/sport2cz.php"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

# ----------------------------
# 🔎 STREAM DETECTION (SAFE VERSION)
# ----------------------------

def extract_urls(html):
    return re.findall(r'https?://[^\s"\'<>]+', html)


def is_direct_m3u8(url: str) -> bool:
    try:
        return ".m3u8" in urlparse(url).path
    except:
        return False


def score(url, ctx=""):
    u = url.lower()
    c = ctx.lower()
    s = 0

    if ".m3u8" in u:
        s += 60
    if ".mpd" in u:
        s += 40

    if "jwt=" in u or "token=" in u:
        s += 20

    if any(x in u for x in ["stream", "hls", "cdn", "video"]):
        s += 10

    if any(x in u for x in ["ads", "google", "doubleclick"]):
        s -= 50

    if any(x in c for x in ["video", "source", "hls", "m3u8"]):
        s += 10

    return s


def static_detect(html):
    urls = extract_urls(html)

    best = None
    best_score = 0

    for url in urls:
        idx = html.find(url)
        ctx = html[max(0, idx - 120): idx + 120]

        s = score(url, ctx)

        if s > best_score:
            best = url
            best_score = s

    return best, best_score


def detect_stream(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)

        # 1) STATIC ANALYSIS
        best, sc = static_detect(r.text)

        if best and sc > 50:
            return best

        # 2) DIRECT SCAN fallback
        urls = extract_urls(r.text)
        for u in urls:
            if ".m3u8" in u:
                return u

        return None

    except:
        return None


# ----------------------------
# 🌐 ROUTES
# ----------------------------

@app.route("/")
def home():
    return "IPTV Stream Detector running (Vercel SAFE MODE)"


@app.route("/playlist.m3u")
def playlist():
    base = request.host_url.rstrip("/")
    out = "#EXTM3U\n"

    for cid, info in CHANNELS.items():
        out += f"#EXTINF:-1,{info[0]}\n"
        out += f"{base}/play/{cid}\n"

    return Response(out, mimetype="text/plain")


@app.route("/play/<cid>")
def play(cid):
    if cid not in CHANNELS:
        return "Kanál neexistuje", 404

    url = CHANNELS[cid][1]

    # 1) přímý m3u8 (včetně jwt)
    if is_direct_m3u8(url):
        return redirect(url, 302)

    # 2) detekce
    stream = detect_stream(url)

    if stream:
        return redirect(stream, 302)

    return "Stream nenalezen", 404


def handler(request):
    return app
