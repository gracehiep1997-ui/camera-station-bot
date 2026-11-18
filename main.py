import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Thông tin cấu hình từ shop Camera Station
PAGE_ACCESS_TOKEN = "EAAeZApvnscPUBTJMuyyRZBlGBGJjkaY3XhySv5o30sJFCpLeYUOVIIVHdZBWkfVtn3tE4oVxE7WB74IJxT0WJ1NLZC9dax0v5cWvtHq4NN7anrvZClldC9j9nWFuoaKOJd3W64ksvUlb6hae4v2EBAE4CFtvSG1zQI89N5lnDSBAmZC1aVrQ9NdKOHb0ZCIVvNM4NqQTgZDZD"
VERIFY_TOKEN = "camerastation_new_2026" # Token mới để tránh cache của Facebook
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwREgD6Dry-KFKHIh8AmwhzfL8yNDISUKHhbJC-U4KBBpur3cc6kIFUttNOyaTbnDsn-Q/exec"

@app.route("/", methods=["GET"])
def home():
    return "Camera Station Bot is running!", 200

# Endpoint xác minh Webhook với Facebook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Hello World", 200

# Endpoint nhận tin nhắn thực tế từ khách hàng gửi đến Fanpage/Instagram
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                
                # Kiểm tra nếu khách gửi tin nhắn văn bản
                if messaging_event.get("message") and messaging_event["message"].get("text"):
                    message_text = messaging_event["message"]["text"]
                    
                    # Phản hồi tự động tư vấn và báo giá cơ bản cho shop
                    reply_text = f"Chào bạn! Camera Station đã nhận được tin nhắn: '{message_text}'. Shop chuyên cho thuê các dòng Fujifilm (X-S20, X-S10, X-M5) và Canon (R50, 600D) thủ tục nhanh gọn chỉ cần CCCD/VNeID + cọc ạ!"
                    
                    # Gửi tin nhắn trả lời khách qua Facebook Messenger API
                    send_message(sender_id, reply_text)
                    
    return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
