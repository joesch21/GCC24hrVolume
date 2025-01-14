from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__, template_folder="../templates")

@app.route('/')
def home():
    # ✅ Debug check to confirm template path
    print(f"Templates Path: {app.template_folder}")
    return render_template('index.html')

# Function to fetch GCC volume and price from CoinBrain API
def get_gcc_volume_from_api():
    url = "https://api.coinbrain.com/public/coin-info"
    headers = {'Content-Type': 'application/json'}
    payload = {"56": ["0x092aC429b9c3450c9909433eB0662c3b7c13cF9A"]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) == 0:
            return {"error": "Unexpected API response structure."}
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data: {e}"}

# Function to calculate staking rewards
def calculate_staking_rewards(data):
    try:
        volume_24h_usd = data[0].get('volume24hUsd', 0)
        price_usd = data[0].get('priceUsd', 0)
        staking_rewards_usd = volume_24h_usd * 0.01
        staking_rewards_gcc = staking_rewards_usd / price_usd if price_usd > 0 else 0
        return volume_24h_usd, staking_rewards_usd, staking_rewards_gcc
    except (KeyError, TypeError, IndexError) as e:
        return {"error": f"Error calculating staking rewards: {e}"}

# API Endpoint for Staking Report
@app.route('/api/staking', methods=['GET'])
def staking_report():
    data = get_gcc_volume_from_api()
    if "error" in data:
        return jsonify(data), 500

    results = calculate_staking_rewards(data)
    if isinstance(results, dict) and "error" in results:
        return jsonify(results), 500

    return jsonify({
        "24h Trading Volume (USD)": results[0],
        "1% Staking Rewards (USD)": results[1],
        "1% Staking Rewards (GCC)": results[2]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
