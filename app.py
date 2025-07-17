@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    print("====== Incoming from Dialogflow ======")
    print(req)

    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    query_text = req.get("queryResult", {}).get("queryText", "").strip()

    if intent_name == "SearchServiceCenter":
        print("🔥 Intent matched: SearchServiceCenter")
        
        matches = []
        for row in data[1:]:  # ข้าม header
            if any(query_text in str(cell) for cell in row):
                matches.append(row)

        if not matches:
            return jsonify({
                "fulfillmentText": f"ไม่พบข้อมูลสำหรับ '{query_text}' ค่ะ"
            })

        # แสดงเฉพาะ 3 รายการแรกเพื่อความกระชับ
        response_lines = []
        for match in matches[:3]:
            response_lines.append(
                f"{match[3]}\nที่อยู่: {match[4]}\nติดต่อ: {match[5]}\nเวลาทำการ: {match[6]}"
            )

        return jsonify({
            "fulfillmentText": "\n\n".join(response_lines)
        })

    return jsonify({
        "fulfillmentText": "ยังไม่มีคำตอบสำหรับ intent นี้ครับ"
    })
