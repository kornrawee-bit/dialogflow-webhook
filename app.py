from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# โหลดข้อมูลจาก CSV (ตรวจสอบว่าไฟล์อยู่ที่ D:\ และตั้งชื่อว่า ASP Profile.csv)
df = pd.read_csv("ASP Profile.csv")

# ฟังก์ชันค้นหาศูนย์บริการ
def search_centers(keyword):
    keyword = keyword.strip().lower()
    results = []

    for _, row in df.iterrows():
        province = str(row['province_th']).lower()
        amphur = str(row['amphur_th']).lower()
        tambon = str(row.get('tambon_th', '')).lower()
        name = str(row['name_th']).lower()

        if any(k in name for k in keyword.split()) or keyword in province or keyword in amphur or keyword in tambon:
            results.append({
                "name": row['name_th'],
                "address": row['address_th'],
                "working_day": row['working_day'],
                "working_time": row['working_time'],
                "contact": row['contact_admin'],
                "product": row.get('service_product_category', '-')
            })

    return results[:10]

# Webhook สำหรับ Dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    user_input = req['queryResult']['queryText']

    results = search_centers(user_input)

    if not results:
        return jsonify({"fulfillmentText": f"ไม่พบศูนย์บริการในพื้นที่ '{user_input}' ค่ะ"})

    reply_lines = []
    for r in results:
        reply = (
            f"📍 *{r['name']}*\n"
            f"📌 ที่อยู่: {r['address']}\n"
            f"🕒 เวลาทำการ: {r['working_day']} {r['working_time']}\n"
            f"📞 ติดต่อ: {r['contact']}\n"
            f"🔧 Service Product Category: {r['product']}"
        )
        reply_lines.append(reply)

    return jsonify({
        "fulfillmentText": "\n\n".join(reply_lines)
    })

# Endpoint ทดสอบ
@app.route('/')
def home():
    return "✅ Flask is running!"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
