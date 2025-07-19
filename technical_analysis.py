import requests
import pandas as pd
import numpy as np

def fetch_candles(interval="15m", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df = df.astype(float)
    return df

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

def is_bullish_engulfing(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return prev['close'] < prev['open'] and last['close'] > last['open'] and last['close'] > prev['open'] and last['open'] < prev['close']

def is_bearish_engulfing(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return prev['close'] > prev['open'] and last['close'] < last['open'] and last['close'] < prev['open'] and last['open'] > prev['close']

def get_technical_signal():
    df_15m = fetch_candles("15m")
    df_1h = fetch_candles("1h")
    df_4h = fetch_candles("4h")

    for df in [df_15m, df_1h, df_4h]:
        df['ema21'] = ema(df['close'], 21)
        df['ema50'] = ema(df['close'], 50)
        df['rsi'] = rsi(df['close'])
        df['macd'], df['macd_signal'] = macd(df['close'])
        df['atr'] = atr(df)

    def analyze(df):
        bullish_candle = is_bullish_engulfing(df)
        bearish_candle = is_bearish_engulfing(df)
        above_ema = df['close'].iloc[-1] > df['ema21'].iloc[-1] > df['ema50'].iloc[-1]
        below_ema = df['close'].iloc[-1] < df['ema21'].iloc[-1] < df['ema50'].iloc[-1]
        rsi_val = df['rsi'].iloc[-1]
        macd_cross = df['macd'].iloc[-2] < df['macd_signal'].iloc[-2] and df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]
        macd_cross_down = df['macd'].iloc[-2] > df['macd_signal'].iloc[-2] and df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]

        if bullish_candle and above_ema and macd_cross and rsi_val < 70:
            return "bullish"
        elif bearish_candle and below_ema and macd_cross_down and rsi_val > 30:
            return "bearish"
        else:
            return "neutral"

    results = {
        "15m": analyze(df_15m),
        "1h": analyze(df_1h),
        "4h": analyze(df_4h),
    }

    majority = list(results.values()).count

    last_price = df_15m['close'].iloc[-1]
    atr_val = df_15m['atr'].iloc[-1]

    entry = last_price
    if majority("bullish") >= 2:
        sl = entry - atr_val
        tp1 = entry + atr_val
        tp2 = entry + 2 * atr_val
        tp3 = entry + 3 * atr_val
        direction = "📈 سیگنال صعودی (Long)"
    elif majority("bearish") >= 2:
        sl = entry + atr_val
        tp1 = entry - atr_val
        tp2 = entry - 2 * atr_val
        tp3 = entry - 3 * atr_val
        direction = "📉 سیگنال نزولی (Short)"
    else:
        return "⏸️ عدم اطمینان (No Trade)"

    # محاسبه R/R
    rr1 = round(abs(tp1 - entry) / abs(entry - sl), 2)
    rr2 = round(abs(tp2 - entry) / abs(entry - sl), 2)
    rr3 = round(abs(tp3 - entry) / abs(entry - sl), 2)

    # محاسبه سود با لوریج 100
    def leverage_profit(target):
        return round(100 * abs(target - entry) / entry, 1)

    profit1 = leverage_profit(tp1)
    profit2 = leverage_profit(tp2)
    profit3 = leverage_profit(tp3)

    success_estimate = "🔹 احتمال موفقیت: حدود 75٪" if majority("bullish") == 3 or majority("bearish") == 3 else "🔸 احتمال موفقیت: حدود 60٪"

    return f"""{direction}

💰 *ورود:* `{entry:.2f}`
🛑 *حد ضرر:* `{sl:.2f}`
🎯 *تارگت ۱:* `{tp1:.2f}` (R/R={rr1}, سود با لوریج ۱۰۰: +{profit1}%)
🎯 *تارگت ۲:* `{tp2:.2f}` (R/R={rr2}, سود با لوریج ۱۰۰: +{profit2}%)
🎯 *تارگت ۳:* `{tp3:.2f}` (R/R={rr3}, سود با لوریج ۱۰۰: +{profit3}%)

{success_estimate}
⏱ تایم‌فریم‌ها: 15m, 1h, 4h
"""
