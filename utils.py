import requests

def send_telegram_message(text, token, chat_id):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("⛔ ارسال پیام به تلگرام ناموفق بود:", e)
