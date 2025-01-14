from flask import Flask, render_template
import requests
import os

app = Flask(__name__, template_folder="../templates")

# Function to fetch GCC volume and price from CoinBrain API
def get_gcc_volume_from_api():
    url = "https://api.coinbrain.com/public/coin-info"
    headers = {'Content-Type': 'application/json'}
    payload = {"56": ["0x092aC429b9c3450c9909433eB0662c3b7c13cF9A"]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
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

# ✅ Serve the index page and display data
@app.route('/')
def home():
    data = get_gcc_volume_from_api()
    if "error" in data:
        return render_template('index.html', error=data['error'])

    results = calculate_staking_rewards(data)
    if isinstance(results, dict) and "error" in results:
        return render_template('index.html', error=results['error'])

    # Send data to the HTML page
    return render_template('index.html',
                           volume_24h_usd=results[0],
                           staking_rewards_usd=results[1],
                           staking_rewards_gcc=results[2])


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

