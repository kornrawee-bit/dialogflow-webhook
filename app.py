from flask import Flask, request, jsonify

app = Flask(__name__)  # ← ต้องอยู่ก่อนถึงจะใช้ @app.route ได้

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    print("====== Incoming from Dialogflow ======")
    print(req)

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    
    if intent_name == "SearchServiceCenter":
        print("🔥 Intent matched: SearchServiceCenter")
        return jsonify({
            "fulfillmentText": "กำลังค้นหาข้อมูลศูนย์บริการ..."
        })

    return jsonify({
        "fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
