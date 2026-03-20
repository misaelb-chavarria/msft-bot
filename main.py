import os
import logging
import yfinance as yf
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN   = os.environ.get("BOT_TOKEN", "8668662179:AAEZX1AUojbZa2x1e7U3lmBnzrf7Fl6NDzo")
CHAT_ID = os.environ.get("CHAT_ID", "7945556811")
TICKER  = "MSFT"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Error: {e}")
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
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

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching real-time data...")
    d = get_msft_data()
    if not d:
        await update.message.reply_text("Error fetching data. Try again.")
        return
    sign = "+" if d["change"] >= 0 else ""
    arrow = "UP" if d["change"] >= 0 else "DOWN"
    await update.message.reply_text(
        f"Microsoft (MSFT) - Live Price\n{d['time']}\n\n"
        f"Price:      ${d['price']:.2f}  {arrow}\n"
        f"Change:     {sign}${d['change']:.2f} ({sign}{d['change_pct']:.2f}%)\n"
        f"Open:       ${d['open']:.2f}\n"
        f"Prev Close: ${d['prev']:.2f}\n"
        f"Day High:   ${d['high']:.2f}\n"
        f"Day Low:    ${d['low']:.2f}"
    )

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Building summary...")
    d = get_msft_data()
    if not d:
        await update.message.reply_text("Error fetching data. Try again.")
        return
    sign = "+" if d["change"] >= 0 else ""
    sign_ath = "+" if d["from_ath"] >= 0 else ""
    await update.message.reply_text(
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

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Analyzing signals...")
    d = get_msft_data()
    if not d:
        await update.message.reply_text("Error fetching data. Try again.")
        return
    sig, desc = get_signal(d)
    await update.message.reply_text(
        f"MSFT Trading Signal\n{d['time']}\n\n"
        f"Signal: {sig}\n{desc}\n\n"
        f"Price:  ${d['price']:.2f}\n"
        f"MA50:   ${d['ma50']:.2f} - {'ABOVE' if d['price'] > d['ma50'] else 'BELOW'}\n"
        f"MA200:  ${d['ma200']:.2f} - {'ABOVE' if d['price'] > d['ma200'] else 'BELOW'}\n\n"
        f"Note: Informational only, not financial advice."
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
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

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    price_kw   = ["price","precio","vale","worth","cuanto","how much","trading","value","cost"]
    high_kw    = ["52","week high","alto","maximo","highest"]
    low_kw     = ["week low","bajo","minimo","lowest"]
    ma_kw      = ["average","promedio","ma50","ma200","moving","200","50 day"]
    cap_kw     = ["market cap","capitalizacion","trillion","cap"]
    signal_kw  = ["signal","buy","sell","trend","comprar","vender"]
    history_kw = ["history","historia","ipo","1986","nadella"]
    summary_kw = ["summary","resumen","full","completo","all"]
    d = None

    if any(k in text for k in price_kw):
        d = get_msft_data()
        if d:
            sign = "+" if d["change"] >= 0 else ""
            arrow = "UP" if d["change"] >= 0 else "DOWN"
            msg = (f"Microsoft (MSFT) right now:\n\nPrice:  ${d['price']:.2f}  {arrow}\n"
                   f"Change: {sign}${d['change']:.2f} ({sign}{d['change_pct']:.2f}%)\nAs of: {d['time']}")
        else:
            msg = "Could not fetch price. Try again."
    elif any(k in text for k in high_kw):
        d = get_msft_data()
        msg = (f"MSFT 52-Week Range:\nHigh: ${d['wk52h']:.2f}\nLow: ${d['wk52l']:.2f}\nNow: ${d['price']:.2f}") if d else "Error."
    elif any(k in text for k in low_kw):
        d = get_msft_data()
        msg = (f"MSFT 52-Week Low:\nLow: ${d['wk52l']:.2f}\nHigh: ${d['wk52h']:.2f}\nNow: ${d['price']:.2f}") if d else "Error."
    elif any(k in text for k in ma_kw):
        d = get_msft_data()
        if d:
            msg = (f"MSFT Moving Averages:\n\nCurrent: ${d['price']:.2f}\n"
                   f"MA50:    ${d['ma50']:.2f} - {'ABOVE' if d['price'] > d['ma50'] else 'BELOW'}\n"
                   f"MA200:   ${d['ma200']:.2f} - {'ABOVE' if d['price'] > d['ma200'] else 'BELOW'}")
        else:
            msg = "Error."
    elif any(k in text for k in cap_kw):
        d = get_msft_data()
        msg = f"MSFT Market Cap: ${d['mktcap']/1e12:.2f} Trillion" if d else "Error."
    elif any(k in text for k in signal_kw):
        d = get_msft_data()
        if d:
            sig, desc = get_signal(d)
            msg = f"MSFT Signal: {sig}\n{desc}"
        else:
            msg = "Error."
    elif any(k in text for k in history_kw):
        msg = ("MSFT Key Milestones:\n\n1986 IPO: $0.09\n1999 Peak: $59.56\n"
               "2009 Bottom: $15.15\n2014 Satya Nadella CEO\n2024 ATH: $467.56\nReturn: +422,000%")
    elif any(k in text for k in summary_kw):
        d = get_msft_data()
        if d:
            sign = "+" if d["change"] >= 0 else ""
            msg = (f"MSFT Summary:\n\nPrice: ${d['price']:.2f}\nChange: {sign}{d['change_pct']:.2f}%\n"
                   f"Cap: ${d['mktcap']/1e12:.2f}T\nMA50: ${d['ma50']:.2f}\nMA200: ${d['ma200']:.2f}\n"
                   f"52W Hi: ${d['wk52h']:.2f}\n52W Lo: ${d['wk52l']:.2f}")
        else:
            msg = "Error."
    else:
        msg = ("I can answer questions about Microsoft (MSFT).\n\nTry:\n"
               "- What is the price of Microsoft today?\n"
               "- What is the 52-week high?\n"
               "- Is MSFT above the 200-day average?\n\n"
               "Or use: /price /summary /signal /history")

    await update.message.reply_text(msg)

def main():
    print("MSFT Intelligence Bot - Starting...")
    print(f"Token: {TOKEN[:20]}...")
    print(f"Chat ID: {CHAT_ID}")
    print("Bot is running. Press Ctrl+C to stop.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("price",   price))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("signal",  signal))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("help",    help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
