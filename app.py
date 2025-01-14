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
            # ✅ Calculate GCC traded volume and rewards
            total_usd_volume = sum([data[0].get('volume24hUsd', 0)])
            data[0]['gccTradedVolume'] = total_usd_volume / data[0].get('priceUsd', 1)
            data[0]['rewardTokenHolders'] = data[0]['gccTradedVolume'] * 0.01
            data[0]['rewardNFTHolders'] = data[0]['gccTradedVolume'] * 0.01
            latest_data = data[0]
            print("✅ Data updated successfully!")
        else:
            print("❌ Failed to fetch data.")
        time.sleep(86400)  # 24 hours = 86400 seconds

@app.route('/')
def home():
    # ✅ Serve the latest stored data
    if not latest_data:
        return render_template('index.html', data=None)
    return render_template('index.html', data=latest_data)

# Function to fetch GCC volume and price from CoinBrain API
def get_gcc_volume_from_api():
    url = "https://api.coinbrain.com/public/coin-info"
    headers = {'Content-Type': 'application/json'}
    payload = {"56": ["0x092aC429b9c3450c9909433eB0662c3b7c13cF9A"]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

if __name__ == "__main__":
    # ✅ Start the background thread for periodic updates
    data_updater = threading.Thread(target=fetch_data_periodically, daemon=True)
    data_updater.start()
    app.run(host="0.0.0.0", port=10000, debug=True)
