from technical_analysis import get_technical_signal
from fundamental_analysis import get_fundamental_signal
from config import TELEGRAM_CHAT_ID, TELEGRAM_BOT_TOKEN
from utils import send_telegram_message

def main():
    tech_signal = get_technical_signal()
    fund_signal = get_fundamental_signal()
    final_signal = "⛏️ سیگنال ترکیبی بیت‌کوین:\n"
    final_signal += f"📊 تحلیل تکنیکال: {tech_signal}\n"
    final_signal += f"🧠 تحلیل فاندامنتال: {fund_signal}"
    send_telegram_message(final_signal, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

if __name__ == "__main__":
    main()
