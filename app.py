from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

def get_answer(user_input):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key('YOUR_SHEET_ID').worksheet('Sheet1')  # หรือใช้ open('ชื่อไฟล์')
    data = sheet.get_all_records()

    for row in data:
        for i in range(1, 3):  # Keyword 1 - 2
            keyword = row.get(f'KEYWORD {i}', '').lower()
            if keyword and keyword in user_input.lower():
                return row.get('ANSWER 1', 'ไม่พบคำตอบ')

    return 'ขออภัย ไม่พบข้อมูลค่ะ'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    user_input = req.get('queryResult', {}).get('queryText', '')
    answer = get_answer(user_input)
    return jsonify({'fulfillmentText': answer})

@app.route('/', methods=['GET'])
def home():
    return 'Webhook is running.'

if __name__ == '__main__':
    app.run()