from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# โหลดไฟล์ service center
df = pd.read_csv("ASP Profile.csv")

@app.route("/", methods=["GET"])
def home():
    return "Webhook is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    
    if intent == "SearchServiceCenter":
        geo_state = req.get("queryResult", {}).get("parameters", {}).get("geo-state", "")
        result = df[df["Province"].str.contains(geo_state, case=False, na=False)]

        if not result.empty:
            messages = []
            for _, row in result.iterrows():
                message = f"{row['Company Name']} ({row['Province']} - {row['District']})\nTel: {row['Tel']}"
                messages.append(message)
            reply = "\n\n".join(messages)
        else:
            reply = f"ขออภัย ไม่พบศูนย์บริการในจังหวัด {geo_state} ค่ะ"

        return jsonify({"fulfillmentText": reply})
    
    return jsonify({"fulfillmentText": "ไม่เข้าใจคำขอค่ะ"})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
