from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# เชื่อมต่อ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service-account.json", scope)
client = gspread.authorize(creds)

# เปิด Google Sheet: ชื่อไฟล์คือ CC CHAT BOT 2025
sheet = client.open("CC CHAT BOT 2025").sheet1

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    if intent_name == "SearchServiceCenter":
        province = parameters.get("geo-state")  # เช่น "Chiang Mai"
        if not province:
            return jsonify({"fulfillmentText": "กรุณาระบุจังหวัดเพื่อค้นหาศูนย์บริการค่ะ"})

        # อ่านข้อมูลทั้งหมดจาก Sheet
        records = sheet.get_all_records()
        matched = [r for r in records if r["province_th"].strip() == province.strip()]

        if not matched:
            return jsonify({"fulfillmentText": f"ไม่พบศูนย์บริการในจังหวัด {province} ค่ะ"})

        # ตอบกลับแบบย่อ 3 รายการแรก
        reply = ""
        for r in matched[:3]:
            reply += f"🏢 {r['name_th']}\n📍 {r['address_th']}\n📞 {r['telephone']}\n🕒 {r['working_day']} {r['working_time']}\n\n"

        return jsonify({"fulfillmentText": reply.strip()})

    return jsonify({"fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
