import requests

def get_fear_and_greed_index():
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        value = int(data['data'][0]['value'])
        classification = data['data'][0]['value_classification']
        return value, classification
    except Exception as e:
        return None, f"خطا در دریافت FGI: {e}"

def get_bitcoin_dominance():
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        btc_dominance = response.json()['data']['market_cap_percentage']['btc']
        return btc_dominance
    except Exception as e:
        return None

def get_fundamental_signal():
    fear_value, fear_class = get_fear_and_greed_index()
    btc_dom = get_bitcoin_dominance()

    signal = ""
    explanations = []

    # تحلیل شاخص ترس و طمع
    if fear_value is not None:
        if fear_value <= 25:
            signal = "🔻 فروش (ترس شدید)"
            explanations.append("بازار در ترس شدید است، احتمال ریزش وجود دارد.")
        elif fear_value <= 45:
            signal = "🟡 احتیاط (ترس)"
            explanations.append("بازار در وضعیت ترس است، ممکن است نوسان کند.")
        elif fear_value <= 60:
            signal = "🟢 خرید (طمع منطقی)"
            explanations.append("بازار در وضعیت منطقی، مناسب برای خرید است.")
        else:
            signal = "🔺 فروش احتمالی (طمع شدید)"
            explanations.append("بازار در طمع شدید است، احتمال اصلاح وجود دارد.")
    else:
        signal = "❓ شاخص ترس و طمع نامشخص"

    # تحلیل دامیننس بیت‌کوین
    if btc_dom is not None:
        explanations.append(f"دامیننس فعلی بیت‌کوین: {btc_dom:.2f}٪")
        if btc_dom > 52:
            explanations.append("دامیننس بالا نشان‌دهنده ورود سرمایه به بیت‌کوین است (ممکن است رشد کند).")
        elif btc_dom < 48:
            explanations.append("دامیننس پایین نشان می‌دهد سرمایه به آلتکوین‌ها رفته؛ مراقب باشید.")
        else:
            explanations.append("دامیننس در محدوده میانه، بازار نوسانی است.")
    else:
        explanations.append("اطلاعات دامیننس در دسترس نیست.")

    return f"{signal}\n\n📉 تحلیل:\n" + "\n".join(explanations)
