from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

app = Flask(__name__)

# ✅ Load credentials from environment variable
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(creds)

# ✅ Open the spreadsheet and specific sheet
sheet = gc.open("CC CHAT BOT 2025").worksheet("ASP Profile")
data = sheet.get_all_records()

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    print("====== Incoming from Dialogflow ======")
    print(json.dumps(req, indent=2, ensure_ascii=False))

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})
    province = parameters.get("geo-state", "").strip()

    if intent_name == "SearchServiceCenter":
        print("🔥 Intent matched: SearchServiceCenter")
        print("📍 Province received:", province)

        # ✅ ค้นหาในหลายคอลัมน์
        search_columns = ["name_th", "amphur_th", "province_th", "service_area", "tambon_th"]
        matched = []
        for row in data:
            for col in search_columns:
                if province in str(row.get(col, "")):
                    matched.append(row)
                    break  # ไม่ต้องเช็คคอลัมน์อื่นถ้าเจอแล้ว

        if matched:
            reply = ""
            for m in matched[:3]:  # จำกัดผลลัพธ์ 3 รายการ
                name = m.get("name_th", "-")
                address = m.get("address_th", "-")
                phone = m.get("telephone", "-")
                hours = m.get("working_time", "-")
                emails = m.get("email", "-")
                region = m.get("region_th", "-")

                reply += f"🏢 {name}\n📍 {address}\n📞 {phone}\n🕒 {hours}\n📧 {emails}\n🌐 {region}\n\n"
        else:
            reply = f"ขออภัย ไม่พบศูนย์บริการที่เกี่ยวข้องกับคำว่า '{province}' ค่ะ"

        return jsonify({"fulfillmentText": reply})

    return jsonify({"fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"})

if __name__ == "__main__":
    app.run(debug=False, port=10000, host="0.0.0.0")
