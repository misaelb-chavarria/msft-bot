import os
import logging
import requests
import yfinance as yf
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────
TOKEN   = os.environ.get("BOT_TOKEN", "8668662179:AAEZX1AUojbZa2x1e7U3lmBnzrf7Fl6NDzo")
CHAT_ID = os.environ.get("CHAT_ID", "7945556811")
TICKER  = "MSFT"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ── TELEGRAM HELPERS ──────────────────────────────────────────
def send_message(chat_id, text):
    try:
        requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception as e:
        logger.error(f"Send error: {e}")

def get_updates(offset=None):
    try:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except Exception as e:
        logger.error(f"GetUpdates error: {e}")
        return []

# ── STOCK DATA ────────────────────────────────────────────────
def get_msft_data():
    try:
        stock = yf.Ticker(TICKER)
        info  = stock.info
        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev    = info.get("previousClose", 0)
        open_p  = info.get("open") or info.get("regularMarketOpen", 0)
        high    = info.get("dayHigh") or info.get("regularMarketDayHigh", 0)
        low     = info.get("dayLow") or info.get("regularMarketDayLow", 0)
        volume  = info.get("volume") or info.get("regularMarketVolume", 0)
        mktcap  = info.get("marketCap", 0)
        wk52h   = info.get("fiftyTwoWeekHigh", 0)
        wk52l   = info.get("fiftyTwoWeekLow", 0)
        ma50    = info.get("fiftyDayAverage", 0)
        ma200   = info.get("twoHundredDayAverage", 0)
        change     = current - prev
        change_pct = (change / prev * 100) if prev else 0
        return {
            "price": current, "prev": prev, "open": open_p,
            "high": high, "low": low, "volume": volume,
            "mktcap": mktcap, "wk52h": wk52h, "wk52l": wk52l,
            "ma50": ma50, "ma200": ma200,
            "change": change, "change_pct": change_pct,
            "from_ath": ((current - 467.56) / 467.56 * 100),
            "from_ipo": ((current - 0.0972) / 0.0972 * 100),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception as e:
        logger.error(f"Stock error: {e}")
        return None

def get_signal(d):
    p, m50, m200 = d["price"], d["ma50"], d["ma200"]
    if p > m50 and p > m200 and m50 > m200:
        return "BULLISH", "Price above MA50 and MA200. Golden Cross active."
    elif p < m50 and p < m200:
        return "BEARISH", "Price below MA50 and MA200. Watch for support."
    elif p > m200 and p < m50:
        return "NEUTRAL", "Above MA200 but below MA50. Correction phase."
    return "CAUTION", "Mixed signals. Monitor closely."

# ── COMMAND HANDLERS ──────────────────────────────────────────
def handle_start(chat_id):
    send_message(chat_id,
        "Microsoft Stock Intelligence Bot\n"
        "Built by Misael De Paz - Data Analyst\n\n"
        "Commands:\n"
        "/price   - Current MSFT price\n"
        "/summary - Full market summary\n"
        "/signal  - Trading signal\n"
        "/history - Key milestones\n"
        "/help    - Show commands\n\n"
        "Or ask in plain text:\n"
        "How much is Microsoft today?\n"
        "What is the 52-week high?"
    )

def handle_price(chat_id):
    send_message(chat_id, "Fetching real-time data...")
    d = get_msft_data()
    if not d:
        send_message(chat_id, "Error fetching data. Try again.")
        return
    sign  = "+" if d["change"] >= 0 else ""
    arrow = "UP" if d["change"] >= 0 else "DOWN"
    send_message(chat_id,
        f"Microsoft (MSFT) - Live Price\n{d['time']}\n\n"
        f"Price:      ${d['price']:.2f}  {arrow}\n"
        f"Change:     {sign}${d['change']:.2f} ({sign}{d['change_pct']:.2f}%)\n"
        f"Open:       ${d['open']:.2f}\n"
        f"Prev Close: ${d['prev']:.2f}\n"
        f"Day High:   ${d['high']:.2f}\n"
        f"Day Low:    ${d['low']:.2f}"
    )

def handle_summary(chat_id):
    send_message(chat_id, "Building summary...")
    d = get_msft_data()
    if not d:
        send_message(chat_id, "Error fetching data. Try again.")
        return
    sign     = "+" if d["change"] >= 0 else ""
    sign_ath = "+" if d["from_ath"] >= 0 else ""
    send_message(chat_id,
        f"Microsoft MSFT - Full Summary\n{d['time']}\n\n"
        f"--- PRICE ---\n"
        f"Current:    ${d['price']:.2f}\n"
        f"Change:     {sign}{d['change_pct']:.2f}%\n"
        f"Range:      ${d['low']:.2f} - ${d['high']:.2f}\n\n"
        f"--- MARKET ---\n"
        f"Market Cap: ${d['mktcap']/1e12:.2f}T\n"
        f"Volume:     {d['volume']:,}\n\n"
        f"--- 52-WEEK ---\n"
        f"High:       ${d['wk52h']:.2f}\n"
        f"Low:        ${d['wk52l']:.2f}\n"
        f"From ATH:   {sign_ath}{d['from_ath']:.1f}%\n\n"
        f"--- MOVING AVERAGES ---\n"
        f"MA50:       ${d['ma50']:.2f} - {'ABOVE' if d['price'] > d['ma50'] else 'BELOW'}\n"
        f"MA200:      ${d['ma200']:.2f} - {'ABOVE' if d['price'] > d['ma200'] else 'BELOW'}\n\n"
        f"--- HISTORICAL ---\n"
        f"IPO (1986): $0.09\n"
        f"From IPO:   +{d['from_ipo']:,.0f}%\n"
        f"ATH:        $467.56 (Jul 2024)"
    )

def handle_signal(chat_id):
    send_message(chat_id, "Analyzing signals...")
    d = get_msft_data()
    if not d:
        send_message(chat_id, "Error fetching data. Try again.")
        return
    sig, desc = get_signal(d)
    send_message(chat_id,
        f"MSFT Trading Signal\n{d['time']}\n\n"
        f"Signal: {sig}\n{desc}\n\n"
        f"Price:  ${d['price']:.2f}\n"
        f"MA50:   ${d['ma50']:.2f} - {'ABOVE' if d['price'] > d['ma50'] else 'BELOW'}\n"
        f"MA200:  ${d['ma200']:.2f} - {'ABOVE' if d['price'] > d['ma200'] else 'BELOW'}\n\n"
        f"Note: Informational only, not financial advice."
    )

def handle_history(chat_id):
    send_message(chat_id,
        "Microsoft MSFT - Key Milestones\n\n"
        "1986  IPO at $0.09 per share\n"
        "1990  Windows 3.0 launched\n"
        "1995  Windows 95 - stock explodes\n"
        "1999  Peak $59.56 - dot-com bubble\n"
        "2000  Crash begins - lost decade\n"
        "2009  Bottom at $15.15\n"
        "2014  Satya Nadella becomes CEO\n"
        "2016  Azure becomes market leader\n"
        "2018  $1 Trillion valuation\n"
        "2023  OpenAI $10B investment\n"
        "2024  All Time High $467.56\n\n"
        "Total Return: +422,000%\n"
        "$1,000 in 1986 = $4.2M today"
    )

def handle_help(chat_id):
    send_message(chat_id,
        "MSFT Bot - Commands\n\n"
        "/price   - Live price + change\n"
        "/summary - Full market summary\n"
        "/signal  - Trading signal\n"
        "/history - Historical milestones\n"
        "/help    - This menu\n\n"
        "Plain text questions also work:\n"
        "- What is the price of Microsoft?\n"
        "- What is the 52-week high?\n"
        "- Is MSFT above the 200-day average?"
    )

def handle_text(chat_id, text):
    t = text.lower()
    price_kw   = ["price","precio","vale","worth","cuanto","how much","value","cost","trading"]
    high_kw    = ["52","week high","alto","maximo","highest"]
    low_kw     = ["week low","bajo","minimo","lowest"]
    ma_kw      = ["average","promedio","ma50","ma200","moving","200","50 day"]
    cap_kw     = ["market cap","capitalizacion","trillion","cap"]
    signal_kw  = ["signal","buy","sell","trend","comprar","vender"]
    history_kw = ["history","historia","ipo","1986","nadella"]
    summary_kw = ["summary","resumen","full","completo","all"]

    if any(k in t for k in price_kw):
        handle_price(chat_id)
    elif any(k in t for k in high_kw):
        d = get_msft_data()
        if d:
            send_message(chat_id, f"MSFT 52-Week Range:\nHigh: ${d['wk52h']:.2f}\nLow: ${d['wk52l']:.2f}\nNow: ${d['price']:.2f}")
        else:
            send_message(chat_id, "Error fetching data.")
    elif any(k in t for k in low_kw):
        d = get_msft_data()
        if d:
            send_message(chat_id, f"MSFT 52-Week Low:\nLow: ${d['wk52l']:.2f}\nHigh: ${d['wk52h']:.2f}\nNow: ${d['price']:.2f}")
        else:
            send_message(chat_id, "Error fetching data.")
    elif any(k in t for k in ma_kw):
        d = get_msft_data()
        if d:
            send_message(chat_id,
                f"MSFT Moving Averages:\n\n"
                f"Current: ${d['price']:.2f}\n"
                f"MA50:    ${d['ma50']:.2f} - {'ABOVE' if d['price'] > d['ma50'] else 'BELOW'}\n"
                f"MA200:   ${d['ma200']:.2f} - {'ABOVE' if d['price'] > d['ma200'] else 'BELOW'}"
            )
        else:
            send_message(chat_id, "Error fetching data.")
    elif any(k in t for k in cap_kw):
        d = get_msft_data()
        if d:
            send_message(chat_id, f"MSFT Market Cap: ${d['mktcap']/1e12:.2f} Trillion")
        else:
            send_message(chat_id, "Error fetching data.")
    elif any(k in t for k in signal_kw):
        handle_signal(chat_id)
    elif any(k in t for k in history_kw):
        handle_history(chat_id)
    elif any(k in t for k in summary_kw):
        handle_summary(chat_id)
    else:
        send_message(chat_id,
            "I can answer questions about Microsoft (MSFT).\n\n"
            "Try:\n"
            "- What is the price of Microsoft today?\n"
            "- What is the 52-week high?\n"
            "- Is MSFT above the 200-day average?\n\n"
            "Or use: /price /summary /signal /history"
        )

# ── MAIN POLLING LOOP ─────────────────────────────────────────
def main():
    print("MSFT Intelligence Bot - Starting...")
    print(f"Token: {TOKEN[:20]}...")
    print(f"Chat ID: {CHAT_ID}")
    print("Bot is running. Press Ctrl+C to stop.")

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text    = message.get("text", "")

                if not chat_id or not text:
                    continue

                logger.info(f"Message from {chat_id}: {text}")

                if text == "/start":
                    handle_start(chat_id)
                elif text == "/price":
                    handle_price(chat_id)
                elif text == "/summary":
                    handle_summary(chat_id)
                elif text == "/signal":
                    handle_signal(chat_id)
                elif text == "/history":
                    handle_history(chat_id)
                elif text == "/help":
                    handle_help(chat_id)
                else:
                    handle_text(chat_id, text)

        except KeyboardInterrupt:
            print("Bot stopped.")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")

if __name__ == "__main__":
    main()
