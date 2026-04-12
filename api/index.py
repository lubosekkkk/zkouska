from flask import Flask, redirect, Response
import requests
import re

app = Flask(__name__)

# --- SEZNAM KANÁLŮ (BEZ LOG) ---
# Formát: "id": ["Název v playlistu", "URL stránky nebo m3u8"]
CHANNELS = {
    "oneplay1": ["ONEPLAY SPORT 1", "https://strumyk.cfd/e/gitshop/oneplaysport1.php"],
    "oneplay2": ["ONEPLAY SPORT 2", "https://strumyk.cfd/e/gitshop/oneplaysport2.php"],
    "oneplay3": ["ONEPLAY SPORT 3", "https://strumyk.cfd/e/gitshop/oneplaysport3.php"],
    "oneplay4": ["ONEPLAY SPORT 4", "https://strumyk.cfd/e/gitshop/oneplaysport4.php"],
    "nova1": ["NOVA SPORT 1", "https://strumyk.cfd/e/gitshop/novasport1.php"],
    "nova2": ["NOVA SPORT 2", "https://strumyk.cfd/e/gitshop/novasport2.php"],
    "nova3": ["NOVA SPORT 3", "https://strumyk.cfd/e/gitshop/novasport3.php"],
    "bnova3": ["NOVA SPORT 3 (2)", "https://sites.google.com/view/parecek18/ns6"]
    "nova4": ["NOVA SPORT 4", "https://strumyk.cfd/e/gitshop/novasport4.php"],
    "nova5": ["NOVA SPORT 5", "https://strumyk.cfd/e/gitshop/novasport5.php"],
    "nova6": ["NOVA SPORT 6", "https://strumyk.cfd/e/gitshop/novasport6.php"],
    "ctsport": ["CT SPORT", "https://dlstreams.top/stream/stream-1033.php"],
    "sport1": ["SPORT 1", "https://sportik.lol/e/vip/CZ/sport1sk.php"],
    "sport2": ["SPORT 2", "https://strumyk.cfd/e/vip/CZ/sport2.php"]
}

@app.route('/')
def home():
    return "Multi-Stream Redirector běží! Playlist je na /playlist.m3u"

@app.route('/playlist.m3u')
def get_playlist():
    import flask
    base_url = flask.request.host_url.rstrip('/')
    
    m3u = "#EXTM3U\n"
    for cid, info in CHANNELS.items():
        name = info[0]
        # Jen název bez loga
        m3u += f'#EXTINF:-1, {name}\n'
        m3u += f'{base_url}/play/{cid}\n'
    
    return Response(m3u, mimetype='text/plain')

@app.route('/play/<channel_id>')
def play_channel(channel_id):
    if channel_id not in CHANNELS:
        return "Kanál neexistuje", 404
    
    source_url = CHANNELS[channel_id][1]

    # Pokud je to přímý m3u8 link, rovnou přesměrujeme
    if source_url.endswith('.m3u8'):
         return redirect(source_url, code=302)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': source_url
    }

    try:
        # 1. Načteme webovou stránku
        response = requests.get(source_url, headers=headers, timeout=10)
        html = response.text
        
        # 2. Hledáme m3u8 odkaz s tokenem
        match = re.search(r'https?://[^\s"\'<>]+?\.m3u8\?[^\s"\'<>]+', html)
        
        if match:
            # 3. Přesměrování na čerstvý stream
            return redirect(match.group(0), code=302)
        else:
            return f"M3U8 link pro {channel_id} nebyl nalezen.", 404
            
    except Exception as e:
        return f"Chyba: {str(e)}", 500

def handler(request):
    return app
