from flask import Flask, redirect, Response
import requests
import re

app = Flask(__name__)

# --- SEZNAM KANÁLŮ ---
CHANNELS = {
    "oneplay1": ["ONEPLAY SPORT 1", "https://strumyk.cfd/e/gitshop/oneplaysport1.php"],
    "oneplay2": ["ONEPLAY SPORT 2", "https://strumyk.cfd/e/gitshop/oneplaysport2.php"],
    "oneplay3": ["ONEPLAY SPORT 3", "https://strumyk.cfd/e/gitshop/oneplaysport3.php"],
    "oneplay4": ["ONEPLAY SPORT 4", "https://strumyk.cfd/e/gitshop/oneplaysport4.php"],
    "nova1": ["NOVA SPORT 1", "https://strumyk.cfd/e/gitshop/novasport1.php"],
    "nova2": ["NOVA SPORT 2", "https://strumyk.cfd/e/gitshop/novasport2.php"],
    "nova3": ["NOVA SPORT 3", "https://strumyk.cfd/e/gitshop/novasport3.php"],
    "bnova3": ["NOVA SPORT 3 (2)", "https://sites.google.com/view/parecek18/ns3"],
    "nova4": ["NOVA SPORT 4", "https://strumyk.cfd/e/gitshop/novasport4.php"],
    "nova5": ["NOVA SPORT 5", "https://strumyk.cfd/e/gitshop/novasport5.php"],
    "nova6": ["NOVA SPORT 6", "https://strumyk.cfd/e/gitshop/novasport6.php"],
    "ctsport": ["CT SPORT", "https://dlstreams.top/stream/stream-1033.php"],
    "sport1": ["SPORT 1", "https://abcsport.top/sport1cz.php"],
    "sport2": ["SPORT 2", "https://abcsport.top/sport2cz.php"]
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
        m3u += f'#EXTINF:-1, {info[0]}\n'
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
        'Referer': source_url,
        'Origin': source_url
    }

    try:
        # 1. Pokus: Načtení hlavní stránky
        response = requests.get(source_url, headers=headers, timeout=10)
        html = response.text
        
        # Hledací vzorec pro m3u8 (agresivnější)
        m3u8_regex = r'https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*'
        
        match = re.search(m3u8_regex, html)
        
        # 2. Pokus: Pokud m3u8 není na hlavní stránce, hledáme iframe
        if not match:
            # Hledáme src u iframu
            iframe_match = re.search(r'<iframe [^>]*src="([^"]+)"', html)
            if iframe_match:
                iframe_url = iframe_match.group(1)
                if iframe_url.startswith('//'):
                    iframe_url = 'https:' + iframe_url
                
                # Jdeme do iframu (pokud je to jiná doména, změníme Referer)
                headers['Referer'] = iframe_url
                response = requests.get(iframe_url, headers=headers, timeout=10)
                match = re.search(m3u8_regex, response.text)

        if match:
            # Přesměrování na nalezený link
            return redirect(match.group(0), code=302)
        else:
            return f"M3U8 link pro {channel_id} nebyl nalezen ani v iframe.", 404
            
    except Exception as e:
        return f"Chyba: {str(e)}", 500

def handler(request):
    return app
