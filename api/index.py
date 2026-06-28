from flask import Flask, redirect, Response, request
import re
import requests
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ----------------------------
# 📺 KANÁLY (tvůj seznam)
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
# 🔎 STATIC DETECTOR
# ----------------------------

def extract_urls(html):
    return re.findall(r'https?://[^\s"\'<>]+', html)


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

    if any(x in u for x in ["stream", "hls", "video", "cdn"]):
        s += 10

    if any(x in u for x in ["ads", "google", "doubleclick"]):
        s -= 50

    if any(x in c for x in ["video", "source", "m3u8", "hls"]):
        s += 10

    return s


def static_detect(html):
    urls = extract_urls(html)

    best = None
    best_score = 0

    for url in urls:
        idx = html.find(url)
        ctx = html[max(0, idx-120):idx+120]

        s = score(url, ctx)

        if s > best_score:
            best = url
            best_score = s

    return best, best_score


# ----------------------------
# 🧠 PLAYWRIGHT DETECTOR (JS + network sniff)
# ----------------------------

def playwright_detect(url):
    found = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def on_response(response):
            try:
                if ".m3u8" in response.url or ".mpd" in response.url:
                    found.append(response.url)
            except:
                pass

        page.on("response", on_response)

        try:
            page.goto(url, timeout=20000)
            page.wait_for_timeout(5000)
        except:
            pass

        browser.close()

    return found


# ----------------------------
# 🚀 MASTER DETECTOR
# ----------------------------

def detect_stream(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        # 1) static scan
        best, score = static_detect(r.text)

        if best and score > 50:
            return best

        # 2) JS sniffing
        streams = playwright_detect(url)

        if streams:
            return streams[0]

        return None

    except:
        return None


# ----------------------------
# 🌐 ROUTES
# ----------------------------

@app.route("/")
def home():
    return "ULTRA IPTV Stream Detector running"


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

    # direct m3u8
    if ".m3u8" in url:
        return redirect(url, 302)

    # ultra detection
    stream = detect_stream(url)

    if stream:
        return redirect(stream, 302)

    return "Stream nenalezen", 404


def handler(request):
    return app
