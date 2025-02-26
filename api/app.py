# main_flask.py
from flask import Flask, jsonify, render_template
import requests, threading, time

app = Flask(__name__, template_folder="./templates")

# Global variable for storing the latest data
latest_data = {}

def fetch_data_periodically():
    """Fetch data from the API every 24 hours and store in memory."""
    global latest_data
    while True:
        print("Fetching new data...")
        data = get_gcc_volume_from_api()
        if data and isinstance(data, list) and len(data) > 0:
            # Manually calculate volume, rewards, etc.
            total_usd_volume = data[0].get('volume24hUsd', 0)
            price_usd = data[0].get('priceUsd', 1)
            data[0]['gccTradedVolume'] = total_usd_volume / price_usd
            data[0]['rewardTokenHolders'] = data[0]['gccTradedVolume'] * 0.01
            data[0]['rewardNFTHolders'] = data[0]['gccTradedVolume'] * 0.01
            latest_data = data[0]  # Save to our global variable
            print("✅ Data updated successfully!")
        else:
            print("❌ Failed to fetch data.")
        time.sleep(86400)  # 24 hours = 86400 sec

@app.route('/')
def home():
    """Renders the HTML page with the latest in-memory data."""
    if not latest_data:
        return render_template('index.html', data=None)
    return render_template('index.html', data=latest_data)

@app.route('/api/gcc_volume', methods=['GET'])
def api_gcc_volume():
    """
    Returns the same in-memory data as JSON,
    so other services (like Node) can fetch it.
    """
    if not latest_data:
        return jsonify({"error": "No data available"}), 500

    return jsonify(latest_data)

def get_gcc_volume_from_api():
    """Calls CoinBrain or any external API to fetch raw GCC data."""
    url = "https://api.coinbrain.com/public/coin-info"
    headers = {'Content-Type': 'application/json'}
    payload = {"56": ["0x092aC429b9c3450c9909433eB0662c3b7c13cF9A"]}

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

if __name__ == "__main__":
    # Start the background thread for periodic updates
    updater = threading.Thread(target=fetch_data_periodically, daemon=True)
    updater.start()

    app.run(host="0.0.0.0", port=10000, debug=True)
