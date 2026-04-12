from flask import Flask, redirect, Response
import requests
import re

app = Flask(__name__)

# --- SEZNAM KANÁLŮ S LOGY A URL ---
# Formát: "id": ["Název", "URL (web nebo přímý m3u8)", "Logo URL"]
CHANNELS = {
    "oneplay1": ["ONEPLAY SPORT 1", "https://strumyk.cfd/e/gitshop/oneplaysport1.php", "https://oneplaysport.cz/assets/front/img/channels/ops_1.png"],
    "oneplay2": ["ONEPLAY SPORT 2", "https://strumyk.cfd/e/gitshop/oneplaysport2.php", "https://oneplaysport.cz/assets/front/img/channels/ops_2.png"],
    "oneplay3": ["ONEPLAY SPORT 3", "https://strumyk.cfd/e/gitshop/oneplaysport3.php", "https://oneplaysport.cz/assets/front/img/channels/ops_3.png"],
    "oneplay4": ["ONEPLAY SPORT 4", "https://strumyk.cfd/e/gitshop/oneplaysport4.php", "https://oneplaysport.cz/assets/front/img/channels/ops_4.png?v2"],
    "nova1": ["NOVA SPORT 1", "https://strumyk.cfd/e/gitshop/novasport1.php", "https://upload.wikimedia.org/wikipedia/commons/c/c9/Nova_Sport_1_2024.png"],
    "nova2": ["NOVA SPORT 2", "https://strumyk.cfd/e/gitshop/novasport2.php", "https://upload.wikimedia.org/wikipedia/commons/6/6d/Nova_Sport_2_2024.png"],
    "nova3": ["NOVA SPORT 3", "https://strumyk.cfd/e/gitshop/novasport3.php", "https://upload.wikimedia.org/wikipedia/commons/6/69/Nova_Sport_3_2024.png"],
    "nova4": ["NOVA SPORT 4", "https://strumyk.cfd/e/gitshop/novasport4.php", "https://upload.wikimedia.org/wikipedia/commons/6/6b/Nova_Sport_4_2024.png"],
    "nova5": ["NOVA SPORT 5", "https://strumyk.cfd/e/gitshop/novasport5.php", "https://upload.wikimedia.org/wikipedia/commons/9/9d/Nova_Sport_5_2024.png"],
    "nova6": ["NOVA SPORT 6", "https://strumyk.cfd/e/gitshop/novasport6.php", "https://upload.wikimedia.org/wikipedia/commons/5/56/Nova_Sport_6_2024.png"],
    "ctsport": ["CT SPORT", "https://dlstreams.top/stream/stream-1033.php", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/%C4%8CT_sport_logo_2022.svg/1200px-%C4%8CT_sport_logo_2022.svg.png"],
    "sport1": ["SPORT 1", "https://dlstreams.top/player/stream-1042.php", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Sport1_logo_cz.svg/1200px-Sport1_logo_cz.svg.png"]
}

@app.route('/')
def home():
    return "Multi-Stream Redirector běží! Tvůj playlist s logy je na /playlist.m3u"

@app.route('/playlist.m3u')
def get_playlist():
    import flask
    base_url = flask.request.host_url.rstrip('/')
    
    m3u = "#EXTM3U\n"
    for cid, info in CHANNELS.items():
        name = info[0]
        logo = info[2]
        # Přidání loga do playlistu pomocí tvg-logo
        m3u += f'#EXTINF:-1 tvg-logo="{logo}", {name}\n'
        m3u += f'{base_url}/play/{cid}\n'
    
    return Response(m3u, mimetype='text/plain')

@app.route('/play/<channel_id>')
def play_channel(channel_id):
    if channel_id not in CHANNELS:
        return "Kanál neexistuje", 404
    
    source_url = CHANNELS[channel_id][1]

    # Pokud je to už hotový m3u8 link (nezačíná to na http web), jen přesměrujeme
    if source_url.endswith('.m3u8') and '?' in source_url:
         return redirect(source_url, code=302)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': source_url
    }

    try:
        # 1. Načteme webovou stránku kanálu (např. strumyk.cfd/...)
        response = requests.get(source_url, headers=headers, timeout=10)
        html = response.text
        
        # 2. Hledáme v kódu m3u8 odkaz (včetně JWT tokenu)
        # Hledáme odkazy, které obsahují index.m3u8 nebo mono.ts.m3u8 atd.
        match = re.search(r'https?://[^\s"\'<>]+?\.m3u8\?[^\s"\'<>]+', html)
        
        if match:
            # 3. Přesměrujeme přehrávač na nalezený čerstvý link
            return redirect(match.group(0), code=302)
        else:
            return f"M3U8 link pro {channel_id} nebyl v kódu stránky nalezen.", 404
            
    except Exception as e:
        return f"Chyba serveru: {str(e)}", 500

def handler(request):
    return app
