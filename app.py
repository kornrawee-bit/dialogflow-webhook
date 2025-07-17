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

# ✅ Load Google Sheets
sheet_asp = gc.open("CC CHAT BOT 2025").worksheet("ASP Profile")
data_asp = sheet_asp.get_all_records()

sheet_phone = gc.open("CC CHAT BOT 2025").worksheet("Usefulness Phone")
data_phone = sheet_phone.get_all_records()

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    print("📥 Request:", json.dumps(req, indent=2, ensure_ascii=False))

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    # ✅ รองรับทั้ง geo-city, geo-state, หรือใช้ queryText ตรงๆ
    keyword = (
        parameters.get("geo-city") or 
        parameters.get("geo-state") or 
        req.get("queryResult", {}).get("queryText", "")
    ).strip()

    print("🔍 Keyword:", keyword)

    # ✅ Intent: ค้นหาศูนย์บริการ
    if intent_name == "SearchServiceCenter":
        print("🔥 Intent matched: SearchServiceCenter")

        matched = []
        for row in data_asp:
            for key in ["name_th", "amphur_th", "province_th", "tambon_th", "service_area"]:
                if keyword in str(row.get(key, "")):
                    matched.append(row)
                    break

        if matched:
            reply = ""
            for m in matched[:3]:
                name = m.get("name_th", "-")
                address = m.get("address_th", "-")
                phone = m.get("contact_admin", "-")
                hours = m.get("address_addition", "-")
                region = m.get("region_th", "-")
                email = m.get("contact_email", "-")

                reply += f"🏢 {name}\n📍 {address}\n📞 {phone}\n🕒 {hours}\n📧 {email}\n🗺 {region}\n\n"
        else:
            reply = f"ขออภัย ไม่พบศูนย์บริการที่เกี่ยวข้องกับ “{keyword}” ค่ะ"

        return jsonify({"fulfillmentText": reply})

    # ✅ Intent: ค้นหาเบอร์โทรศัพท์จาก Usefulness Phone
    elif intent_name == "FindUsefulPhone":
        print("🔥 Intent matched: FindUsefulPhone")

        filtered = []
        for row in data_phone:
            combined = f"{row.get('contact_name', '')} {row.get('telephone', '')} {row.get('remarks', '')}"
            if keyword.lower() in combined.lower():
                filtered.append(row)

        if not filtered:
            return jsonify({"fulfillmentText": f"ไม่พบข้อมูลที่เกี่ยวข้องกับ “{keyword}” ค่ะ"})

        messages = []
        for row in filtered[:10]:
            name = row.get("contact_name", "-")
            phone = row.get("telephone", "-")
            remarks = row.get("remarks", "-")
            messages.append(f"📌 {name}\n📞 {phone}\n📝 {remarks}")

        reply_text = "\n\n".join(messages)

        return jsonify({
            "fulfillmentText": reply_text
        })

    # ✅ Default fallback
    return jsonify({"fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"})

if __name__ == "__main__":
    app.run(debug=False, port=10000, host="0.0.0.0")
