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
