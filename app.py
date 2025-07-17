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

# ✅ Load Merged Sheet
sheet = gc.open("CC CHAT BOT 2025").worksheet("Merged Sheet")
data_merged = sheet.get_all_records()

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

    # ✅ เลือกประเภทข้อมูลตาม intent
    category_filter = "ASP" if intent_name == "SearchServiceCenter" else \
                      "PHONE" if intent_name == "FindUsefulPhone" else None

    filtered = [
        row for row in data_merged
        if str(row.get("category", "")).strip().upper() == category_filter
        and any(keyword.lower() in str(row.get(k, "")).lower() for k in row)
    ]

    if not filtered:
        return jsonify({"fulfillmentText": f"ไม่พบข้อมูลที่เกี่ยวข้องกับ “{keyword}” ค่ะ"})

    messages = []
    for row in filtered[:10]:
        if category_filter == "ASP":
            name = row.get("name_th", "-")
            address = row.get("address_th", "-")
            region = row.get("region_th", "-")
            hours = row.get("address_addition", "-")
            email = row.get("contact_email", "-")

            # ✅ รวม contact_admin และ telephone
            phone_admin = row.get("contact_admin", "")
            phone_other = row.get("telephone", "")
            phone = " / ".join(filter(None, [phone_admin, phone_other])) or "-"

            message = f"🏢 {name}\n📍 {address}\n📞 {phone}\n🕒 {hours}\n📧 {email}\n🗺 {region}"
        else:  # PHONE
            name = row.get("contact_name") or row.get("name") or "-"
            phone = row.get("telephone", "-")
            remarks = row.get("remarks", "-")
            message = f"📌 {name}\n📞 {phone}\n📝 {remarks}"

        messages.append(message)

    reply_text = "\n\n".join(messages)

    return jsonify({
        "fulfillmentText": reply_text
    })

if __name__ == "__main__":
    app.run(debug=False, port=10000, host="0.0.0.0")
