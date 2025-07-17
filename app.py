import os
import json
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ ประกาศ Flask ก่อน route
app = Flask(__name__)

# 🔐 Auth Google Sheet จาก Environment Variable
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# 📄 เปิด Sheet และดึงข้อมูล
sheet = gc.open("CC CHAT BOT 2025").worksheet("ASP Profile")
data = sheet.get_all_records()

# ✅ route ต้องตามหลัง app = Flask(...)
@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    keyword = req["queryResult"]["queryText"].strip()

    results = []
    for row in data:
        if any(keyword.lower() in str(value).lower() for value in row.values()):
            # แสดงข้อมูลทั้งหมด พร้อม Region TH และ Contact Email
            contact_email = row.get("Contact Email", "")
            region_th = row.get("Region TH", "")
            response = "\n".join([
                f"ชื่อศูนย์: {row.get('Service Center Name', '')}",
                f"ที่อยู่: {row.get('Address', '')}",
                f"เบอร์ติดต่อ: {row.get('Contact Number', '')}",
                f"เวลาทำการ: {row.get('Working Hour', '')}",
                f"Region: {region_th}",
                f"อีเมล: {contact_email}",
            ])
            results.append(response)

    if results:
        response_text = "\n\n".join(results)
    else:
        response_text = "ไม่พบข้อมูลที่เกี่ยวข้อง"

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run()
