from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])  # รองรับ POST จาก Dialogflow
def webhook():
    req = request.get_json()
    print("Request:", req)  # ดูข้อมูล intent ที่รับมา

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    
    if intent_name == "SearchServiceCenter":
        return jsonify({
            "fulfillmentText": "กำลังค้นหาข้อมูลศูนย์บริการ..."
        })

    return jsonify({
        "fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)  # ต้องระบุ host และ port แบบนี้ให้ Render รู้จัก
