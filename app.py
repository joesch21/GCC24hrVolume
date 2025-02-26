from flask import Flask, jsonify, render_template
import requests
import threading
import time

app = Flask(__name__, template_folder="./templates")

# Global variable to store the latest data
latest_data = {}

def fetch_data_periodically():
    """Fetch data from the API every 24 hours."""
    global latest_data
    while True:
        print("Fetching new data from API...")
        data = get_gcc_volume_from_api()
        if data and isinstance(data, list) and len(data) > 0:
            # data[0] might have keys like "priceUsd", "volume24hUsd", etc. from CoinBrain
            entry = data[0]

            # Manually set or compute additional fields:
            # e.g., address, chainId, etc.
            entry['address'] = "0x092aC429b9c3450c9909433eB0662c3b7c13cF9A"  # If you want to show the GCC contract
            entry['chainId'] = 56  # Because it's BSC mainnet

            total_usd_volume = entry.get('volume24hUsd', 0)
            price_usd = entry.get('priceUsd', 1)

            # Calculate GCC traded volume
            entry['gccTradedVolume'] = total_usd_volume / price_usd
            # Rewards
            entry['rewardTokenHolders'] = entry['gccTradedVolume'] * 0.01
            entry['rewardNFTHolders'] = entry['gccTradedVolume'] * 0.01

            # If you'd like more fields, you can set them here:
            # e.g., placeholder for 24h or 7d changes, or trades in last 24h
            entry.setdefault('priceUsd24hAgo', 0.0)
            entry.setdefault('priceUsd7dAgo', 0.0)
            entry.setdefault('trades24h', 0)
            entry.setdefault('totalReserveUsd', 0.0)
            entry.setdefault('circulatingSupplyUsd', 0.0)
            entry.setdefault('marketCapUsd', 0.0)

            # Now store it in latest_data
            latest_data = entry
            print("✅ Data updated successfully!")
        else:
            print("❌ Failed to fetch data.")
        time.sleep(86400)  # 24 hours = 86400 seconds

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
    # ✅ Start the background thread for periodic updates
    data_updater = threading.Thread(target=fetch_data_periodically, daemon=True)
    data_updater.start()

    app.run(host="0.0.0.0", port=10000, debug=True)
