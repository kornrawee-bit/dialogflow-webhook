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
    province = parameters.get("geo-state", "")

    if intent_name == "SearchServiceCenter":
        print("🔥 Intent matched: SearchServiceCenter")
        print("📍 Province received:", province)

        matched = [row for row in data if province in row.get("service_area", "")]

        if matched:
            reply = ""
            for m in matched[:3]:  # จำกัดที่ 3 รายการแรก
                name = m.get("name_th", "-")
                address = m.get("address_th", "-")
                phone = m.get("telephone", "-")
                hours = m.get("working_time", "-")
                email = m.get("contact_email", "-")       # ✅ เพิ่มอีเมล
                region = m.get("region_th", "-")          # ✅ เพิ่มภูมิภาค
                reply += (
                    f"🏢 {name}\n"
                    f"📍 {address}\n"
                    f"📞 {phone}\n"
                    f"🕒 {hours}\n"
                    f"📧 {email}\n"
                    f"🗺️ {region}\n\n"
                )
        else:
            reply = f"ขออภัย ไม่พบศูนย์บริการในจังหวัด {province} ค่ะ"

        return jsonify({"fulfillmentText": reply})

    return jsonify({"fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"})

if __name__ == "__main__":
    app.run(debug=False, port=10000, host="0.0.0.0")
