from flask import Flask, redirect, Response
import requests
import re

app = Flask(__name__)

# SEM VLOŽ ADRESU STRÁNKY, KDE BĚŽÍ PŘEHRÁVAČ V PROHLÍŽEČI
SOURCE_URL = "https://strumyk.cfd/e/gitshop/oneplaysport1.php"

@app.route('/')
def home():
    return "Stream Redirector is running! Use /stream.m3u8 to play."

@app.route('/stream.m3u8')
def get_stream():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 1. Stáhneme kód stránky
        response = requests.get(SOURCE_URL, headers=headers, timeout=10)
        html = response.text
        
        # 2. Hledáme m3u8 link pomocí regulárního výrazu
        # Tento vzorec hledá cokoliv, co začíná https a končí .m3u8 i s tokenem
        match = re.search(r'https?://[^\s"\'<>]+index\.m3u8\?[^\s"\'<>]+', html)
        
        if match:
            stream_url = match.group(0)
            # 3. Přesměrujeme přehrávač na nalezený link
            return redirect(stream_url, code=302)
        else:
            return "Nepodařilo se najít m3u8 link v kódu stránky.", 404
            
    except Exception as e:
        return f"Chyba: {str(e)}", 500

# Nutné pro Vercel
def handler(request):
    return app
