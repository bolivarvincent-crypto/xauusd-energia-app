from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Backend OK"})

@app.route('/precio')
def precio():
    try:
        url = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD"
        res = requests.get(url, timeout=10).json()

        # Tomamos el primer bloque
        item = res[0]

        # spreadProfilePrices contiene diferentes precios
        first_profile = item["spreadProfilePrices"][0]

        precio = first_profile["bid"]  # O "ask", como prefieras

        return jsonify({"gold_price_usd": precio})

    except Exception as e:
        return jsonify({"error": str(e), "gold_price_usd": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
