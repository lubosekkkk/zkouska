from flask import Flask, redirect, Response, request
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)

# --- KANÁLY ---
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
    "sport2": ["SPORT 2", "https://abcsport.top/sport2cz.php"]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

# --- HELPERS ---

def is_m3u8(url: str) -> bool:
    """Zkontroluje, jestli URL je m3u8 (i s ?jwt=...)"""
    try:
        path = urlparse(url).path
        return path.endswith(".m3u8")
    except:
        return False


def extract_m3u8(text: str):
    """Najde první m3u8 v textu"""
    pattern = r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*'
    return re.search(pattern, text)


def fetch(url: str):
    """Stažení stránky"""
    return requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)


# --- ROUTES ---

@app.route("/")
def home():
    return "Multi Stream API běží. Playlist: /playlist.m3u"


@app.route("/playlist.m3u")
def playlist():
    base = request.host_url.rstrip("/")
    m3u = "#EXTM3U\n"

    for cid, info in CHANNELS.items():
        m3u += f"#EXTINF:-1,{info[0]}\n"
        m3u += f"{base}/play/{cid}\n"

    return Response(m3u, mimetype="text/plain")


@app.route("/play/<channel_id>")
def play(channel_id):
    if channel_id not in CHANNELS:
        return "Kanál neexistuje", 404

    source_url = CHANNELS[channel_id][1]

    try:
        # 1) pokud je to přímo m3u8 (včetně jwt)
        if is_m3u8(source_url):
            return redirect(source_url, 302)

        # 2) načti stránku
        r = fetch(source_url)

        # 3) zkus najít m3u8
        match = extract_m3u8(r.text)

        if match:
            return redirect(match.group(0), 302)

        return "M3U8 nenalezeno", 404

    except Exception as e:
        return f"Chyba: {str(e)}", 500


# --- VERCEL ENTRYPOINT ---
def handler(request):
    return app
