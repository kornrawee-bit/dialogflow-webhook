from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# อ่านข้อมูลไฟล์ CSV ที่อยู่ใน repository
df = pd.read_csv("ASP Profile.csv")

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    parameters = req.get("queryResult", {}).get("parameters", {})
    geo_state = parameters.get("geo-state")

    if not geo_state:
        return jsonify({"fulfillmentText": "ไม่พบข้อมูลจังหวัดที่คุณระบุค่ะ"})

    # กรองข้อมูลตามจังหวัด
    matched_rows = df[df['Province'].str.contains(geo_state, case=False, na=False)]

    if matched_rows.empty:
        return jsonify({"fulfillmentText": f"ไม่พบศูนย์บริการในจังหวัด {geo_state} ค่ะ"})

    reply = ""
    for _, row in matched_rows.iterrows():
        reply += f"📍 {row['Dealer Name']}\nที่อยู่: {row['Address']}\nติดต่อ: {row['Tel']}\nService Product Category: {row['Service Product Category']}\n\n"

    return jsonify({"fulfillmentText": reply.strip()})
