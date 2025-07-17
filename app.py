elif intent_name == "FindUsefulPhone":
    print("🔥 Intent matched: FindUsefulPhone")

    # ✅ กรอง keyword จากข้อความที่ผู้ใช้พิมพ์
    filtered = []
    for row in data_phone:
        combined = f"{row.get('Contact Name', '')} {row.get('Telephone', '')} {row.get('Remarks', '')}"
        if keyword.lower() in combined.lower():
            filtered.append(row)

    print(f"🔎 Found {len(filtered)} matches for keyword '{keyword}'")

    if not filtered:
        return jsonify({"fulfillmentText": f"ไม่พบข้อมูลที่เกี่ยวข้องกับ “{keyword}” ค่ะ"})

    # ✅ สร้างข้อความตอบกลับ
    messages = []
    for row in filtered[:10]:
        name = row.get("Contact Name", "-")
        phone = row.get("Telephone", "-")
        remarks = row.get("Remarks", "-")
        messages.append(f"📌 {name}\n📞 {phone}\n📝 {remarks}")

    reply = "\n\n".join(messages)

    return jsonify({"fulfillmentText": reply})
