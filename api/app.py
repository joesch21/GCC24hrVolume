# server_flask.py (example name)
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    # Renders the HTML with advanced data
    data = get_gcc_volume_from_api()
    if not data:
        return render_template('index.html', data=None)

    # Perform your volume/trading calculations
    data[0]['gccTradedVolume'] = data[0].get('volume24hUsd', 0) / data[0].get('priceUsd', 1)
    data[0]['rewardTokenHolders'] = data[0]['gccTradedVolume'] * 0.01
    data[0]['rewardNFTHolders'] = data[0]['gccTradedVolume'] * 0.01

    return render_template('index.html', data=data[0])

@app.route('/api/gcc_volume', methods=['GET'])
def api_gcc_volume():
    # Returns JSON with the same calculations
    data = get_gcc_volume_from_api()
    if not data:
        return jsonify({"error": "Failed to fetch data"}), 500

    # replicate the calculations done in the home() route
    data[0]['gccTradedVolume'] = data[0].get('volume24hUsd', 0) / data[0].get('priceUsd', 1)
    data[0]['rewardTokenHolders'] = data[0]['gccTradedVolume'] * 0.01
    data[0]['rewardNFTHolders'] = data[0]['gccTradedVolume'] * 0.01

    return jsonify(data[0])

def get_gcc_volume_from_api():
    url = "https://api.coinbrain.com/public/coin-info"
    headers = {'Content-Type': 'application/json'}
    payload = {"56": ["0x092aC429b9c3450c9909433eB0662c3b7c13cF9A"]}

    try:
        r = requests.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    app.run(debug=True)
