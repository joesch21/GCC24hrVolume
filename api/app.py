from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__, template_folder="./templates")

@app.route('/')
def home():
    # This still renders the HTML page
    data = get_gcc_volume_from_api()
    if not data:
        return render_template('index.html', data=None)

    # Do your volume calculations
    data[0]['gccTradedVolume'] = ...
    data[0]['rewardTokenHolders'] = ...
    data[0]['rewardNFTHolders'] = ...

    return render_template('index.html', data=data[0])

# ✅ NEW: Provide a JSON endpoint
@app.route('/api/gcc_volume', methods=['GET'])
def api_gcc_volume():
    data = get_gcc_volume_from_api()
    if not data:
        return jsonify({"error": "Failed to fetch data"}), 500

    # Perform the same calculations
    data[0]['gccTradedVolume'] = ...
    data[0]['rewardTokenHolders'] = ...
    data[0]['rewardNFTHolders'] = ...

    # Return JSON data
    return jsonify(data[0])

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
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
