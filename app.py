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

# ✅ Load merged Google Sheet
sheet = gc.open("CC CHAT BOT 2025").worksheet("ASP Profile")
data_all = sheet.get_all_records()

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    print("📥 Request:", json.dumps(req, indent=2, ensure_ascii=False))

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    keyword = (
        parameters.get("geo-city") or 
        parameters.get("geo-state") or 
        req.get("queryResult", {}).get("queryText", "")
    ).strip()

    print("🔍 Keyword:", keyword)

    filtered = []
    for row in data_all:
        combined = " ".join([str(v) for v in row.values()])
        if keyword.lower() in combined.lower():
            filtered.append(row)

    if not filtered:
        return jsonify({"fulfillmentText": f"ไม่พบข้อมูลที่เกี่ยวข้องกับ “{keyword}” ค่ะ"})

    messages = []
    for row in filtered[:10]:
        category = row.get("category", "").strip().lower()

        if category == "asp":
            name = row.get("name_th", row.get("contact_name", "-"))
            address = row.get("address_th", "-")
            phone_main = row.get("contact_admin", "")
            phone_alt = row.get("telephone", "")
            phones = " / ".join(filter(None, [phone_main, phone_alt]))

            # ✅ รวม working_day, working_time, address_addition
            working_day = row.get("working_day", "")
            working_time = row.get("working_time", "")
            address_add = row.get("address_addition", "")
            hours = " / ".join(filter(None, [working_day, working_time, address_add]))

            email = row.get("contact_email", "-")
            region = row.get("region_th", "-")

            messages.append(f"🏢 {name}\n📍 {address}\n📞 {phones}\n🕒 {hours}\n📧 {email}\n🗺 {region}")
        else:  # PHONE
            name = row.get("name_th", row.get("contact_name", "-"))
            phone = row.get("telephone", "-")
            remarks = row.get("remarks", "-")
            messages.append(f"📌 {name}\n📞 {phone}\n📝 {remarks}")

    reply_text = "\n\n".join(messages)

    return jsonify({"fulfillmentText": reply_text})

if __name__ == "__main__":
    app.run(debug=False, port=10000, host="0.0.0.0")
