import os
import json
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Set up Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# Open the Google Sheet and worksheet
sheet = gc.open("CC CHAT BOT 2025").worksheet("ASP Profile")
data = sheet.get_all_records()

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    keyword = req["queryResult"]["queryText"].strip()

    # Search across all columns
    results = []
    for row in data:
        if any(keyword.lower() in str(value).lower() for value in row.values()):
            # Append Contact Email and Region TH explicitly at the end
            modified_row = dict(row)  # copy
            contact_email = row.get("Contact Email", "")
            region_th = row.get("Region TH", "")
            modified_row["Region TH"] = region_th
            modified_row["Contact Email"] = contact_email
            results.append(modified_row)

    if results:
        response_text = json.dumps(results, ensure_ascii=False, indent=2)
    else:
        response_text = "ไม่พบข้อมูลที่เกี่ยวข้อง"

    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run()
