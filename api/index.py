from flask import Flask, redirect, Response, request
import requests

app = Flask(__name__)

# =========================
# 🔴 BACKEND (Render / Railway)
# =========================
BACKEND_URL = "https://stream-backend-ts5c.onrender.com/find"

# =========================
# 📺 KANÁLY
# =========================
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

# =========================
# 🟢 HOME
# =========================
@app.route("/")
def home():
    return "IPTV system running"

# =========================
# 🟢 PLAYLIST (VLC)
# =========================
@app.route("/playlist.m3u")
def playlist():
    base = request.host_url.rstrip("/")
    m3u = "#EXTM3U\n"

    for cid, info in CHANNELS.items():
        m3u += f"#EXTINF:-1,{info[0]}\n"
        m3u += f"{base}/play/{cid}\n"

    return Response(m3u, mimetype="text/plain")

# =========================
# 🟢 PLAY CHANNEL
# =========================
@app.route("/play/<cid>")
def play(cid):
    if cid not in CHANNELS:
        return "Kanál neexistuje", 404

    url = CHANNELS[cid][1]

    # 1) pokud je přímo m3u8
    if ".m3u8" in url:
        return redirect(url, 302)

    # 2) zavolání backendu (Render Playwright server)
    try:
        r = requests.get(BACKEND_URL, params={"url": url}, timeout=15)
        data = r.json()

        stream = data.get("stream")

        if stream:
            return redirect(stream, 302)

        return "Stream nenalezen", 404

    except Exception as e:
        return f"Backend error: {str(e)}", 500

# =========================
# VERCEL ENTRYPOINT
# =========================
def handler(request):
    return app
