from flask import Flask, render_template, request, jsonify
import requests, json, re, urllib3
from urllib.parse import quote_plus

app = Flask(__name__)

# === API Base URL ===
API_BASE = "https://numapi.anshapi.workers.dev/?num="
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Helper Functions ===
def api_call(number):
    url = API_BASE + quote_plus(number)
    r = requests.get(url, timeout=20, verify=False)
    r.raise_for_status()
    return r.text

def format_result(raw, number):
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "data" in parsed and isinstance(parsed["data"], list):
            data = parsed["data"]
            if not data:
                return f"⚠️ No result found for <b>{number}</b>."
            msg = f"📊 <b>Results for {number}</b><br><br>"
            for idx, d in enumerate(data, 1):
                msg += f"<b>Result {idx}:</b><br><pre>{json.dumps(d, indent=2, ensure_ascii=False)}</pre><br>"
            return msg
        else:
            return f"<pre>{json.dumps(parsed, indent=2, ensure_ascii=False)}</pre>"
    except Exception:
        return f"<pre>{raw}</pre>"

# === Routes ===
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        # Render health-check (no body needed)
        return '', 200
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_number():
    num = request.form.get('number', '').strip()
    if not re.match(r'^\d{10}$', num):
        return jsonify({"error": "❌ Please enter a valid 10-digit number."})
    try:
        raw = api_call(num)
        formatted = format_result(raw, num)
        return jsonify({"result": formatted})
    except Exception as e:
        return jsonify({"error": f"⚠️ API Error: {e}"})

# === Run Locally ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
