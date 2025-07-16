from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# โหลดข้อมูลศูนย์บริการ
df = pd.read_csv('service_centers.csv')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:", req)

    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    if intent == "SearchServiceCenter":
        province = parameters.get("geo-state")
        print("Province received:", province)

        # กรองเฉพาะแถวที่ตรงกับจังหวัด
        result_df = df[df['province'].str.contains(province, case=False, na=False)]

        if not result_df.empty:
            # รวมข้อมูลให้อ่านง่าย
            responses = []
            for _, row in result_df.iterrows():
                response = f"{row['shop_name']} - {row['address']} ({row['tel']})"
                responses.append(response)
            fulfillment_text = "\n".join(responses)
        else:
            fulfillment_text = f"ขออภัย ไม่พบศูนย์บริการในจังหวัด {province} ค่ะ"
    else:
        fulfillment_text = "ไม่เข้าใจคำขอค่ะ"

    return jsonify({"fulfillmentText": fulfillment_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
