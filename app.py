from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# โหลดข้อมูลจาก CSV
df = pd.read_csv("ASP Profile.csv")

@app.route('/')
def home():
    return 'Dialogflow Webhook is running.'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    query = req.get('queryResult').get('queryText')

    # ค้นหาจากจังหวัดหรืออำเภอที่ผู้ใช้ป้อน
    result = df[df.apply(lambda row: query in str(row['Province']) or query in str(row['District']), axis=1)]

    if result.empty:
        response_text = f"ไม่พบข้อมูลศูนย์บริการสำหรับคำค้น '{query}'"
    else:
        lines = []
        for _, row in result.iterrows():
            line = f"""📍 {row['Service Center Name']}
ที่อยู่: {row['Address']}
เวลาทำการ: {row['Working Hour']}
ติดต่อ: {row['Contact']}
Service Product Category: {row['Service Product Category']}"""
            lines.append(line)
        response_text = "\n\n".join(lines)

    return jsonify({"fulfillmentText": response_text})

# ✅ สำหรับ Render.com ต้องระบุ host และ port จาก environment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
