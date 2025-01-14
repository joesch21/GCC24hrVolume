from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__, template_folder="./templates")

@app.route('/')
def home():
    # ✅ Fetch data and ensure values are defined
    data = get_gcc_volume_from_api()
    if "error" in data:
        return render_template('index.html', data=None)
    # ✅ Calculate the total USD volume divided by the price of GCC
    total_usd_volume = sum([data[0].get('volume24hUsd', 0)])
    data[0]['gccTradedVolume'] = total_usd_volume / data[0].get('priceUsd', 1)
    # ✅ Calculate rewards for Token and NFT holders
    data[0]['rewardTokenHolders'] = data[0]['gccTradedVolume'] * 0.01
    data[0]['rewardNFTHolders'] = data[0]['gccTradedVolume'] * 0.01
    # ✅ Pass all data directly to the template
    return render_template('index.html', data=data[0])

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
    app.run(host="0.0.0.0", port=10000, debug=True)
