# ============================================================
# SELIXOR SYSTEMS — Microsoft Stock Intelligence Bot
# Script 3: Telegram Bot + Yahoo Finance Real-Time Data
# Autor: Misael De Paz
# ============================================================
# Instalación requerida (corre esto en tu terminal primero):
# pip install python-telegram-bot yfinance gspread
# ============================================================

import logging
import yfinance as yf
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# ── CONFIGURACIÓN ────────────────────────────────────────────
TOKEN   = "8668662179:AAEZX1AUojbZa2x1e7U3lmBnzrf7Fl6NDzo"
CHAT_ID = "7945556811"
TICKER  = "MSFT"

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── FUNCIÓN: Obtener datos de MSFT ───────────────────────────
def get_msft_data():
    """Obtiene datos actuales de Microsoft desde Yahoo Finance."""
    try:
        stock = yf.Ticker(TICKER)
        info  = stock.info
        hist  = stock.history(period="5d")

        current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev_close    = info.get("previousClose", 0)
        open_price    = info.get("open") or info.get("regularMarketOpen", 0)
        day_high      = info.get("dayHigh") or info.get("regularMarketDayHigh", 0)
        day_low       = info.get("dayLow") or info.get("regularMarketDayLow", 0)
        volume        = info.get("volume") or info.get("regularMarketVolume", 0)
        market_cap    = info.get("marketCap", 0)
        week_52_high  = info.get("fiftyTwoWeekHigh", 0)
        week_52_low   = info.get("fiftyTwoWeekLow", 0)
        ma50          = info.get("fiftyDayAverage", 0)
        ma200         = info.get("twoHundredDayAverage", 0)

        change        = current_price - prev_close
        change_pct    = (change / prev_close * 100) if prev_close else 0
        from_ath      = ((current_price - 467.56) / 467.56 * 100)
        from_ipo      = ((current_price - 0.0972) / 0.0972 * 100)

        return {
            "current_price": current_price,
            "prev_close":    prev_close,
            "open_price":    open_price,
            "day_high":      day_high,
            "day_low":       day_low,
            "volume":        volume,
            "market_cap":    market_cap,
            "week_52_high":  week_52_high,
            "week_52_low":   week_52_low,
            "ma50":          ma50,
            "ma200":         ma200,
            "change":        change,
            "change_pct":    change_pct,
            "from_ath":      from_ath,
            "from_ipo":      from_ipo,
            "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception as e:
        logger.error(f"Error fetching MSFT data: {e}")
        return None

# ── FUNCIÓN: Señal de trading ─────────────────────────────────
def get_signal(data):
    """Genera señal simple basada en precio vs MAs."""
    price = data["current_price"]
    ma50  = data["ma50"]
    ma200 = data["ma200"]

    if price > ma50 and price > ma200 and ma50 > ma200:
        return "BULLISH", "Price above MA50 and MA200. Golden Cross active."
    elif price < ma50 and price < ma200:
        return "BEARISH", "Price below MA50 and MA200. Watch for support."
    elif price > ma200 and price < ma50:
        return "NEUTRAL", "Price above MA200 but below MA50. Correction phase."
    else:
        return "CAUTION", "Mixed signals. Monitor closely."

# ── COMANDO: /start ───────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "Microsoft Stock Intelligence Bot\n"
        "Built by Misael De Paz — Data Analyst\n\n"
        "Available commands:\n\n"
        "/price — Current MSFT price\n"
        "/summary — Full market summary\n"
        "/signal — Trading signal analysis\n"
        "/history — Key historical facts\n"
        "/help — Show all commands\n\n"
        "Or just ask me anything:\n"
        "How much is Microsoft today?\n"
        "What is the 52-week high?\n"
        "Is MSFT above the 200-day average?"
    )
    await update.message.reply_text(welcome)

# ── COMANDO: /price ───────────────────────────────────────────
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching real-time data...")
    data = get_msft_data()
    if not data:
        await update.message.reply_text("Error fetching data. Please try again.")
        return

    arrow = "UP" if data["change"] >= 0 else "DOWN"
    sign  = "+" if data["change"] >= 0 else ""

    msg = (
        f"Microsoft (MSFT) — Live Price\n"
        f"{data['timestamp']}\n\n"
        f"Price:     ${data['current_price']:.2f}  {arrow}\n"
        f"Change:    {sign}${data['change']:.2f} ({sign}{data['change_pct']:.2f}%)\n"
        f"Open:      ${data['open_price']:.2f}\n"
        f"Prev Close: ${data['prev_close']:.2f}\n"
        f"Day High:  ${data['day_high']:.2f}\n"
        f"Day Low:   ${data['day_low']:.2f}"
    )
    await update.message.reply_text(msg)

# ── COMANDO: /summary ─────────────────────────────────────────
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Building full summary...")
    data = get_msft_data()
    if not data:
        await update.message.reply_text("Error fetching data. Please try again.")
        return

    sign_change = "+" if data["change"] >= 0 else ""
    sign_ath    = "+" if data["from_ath"] >= 0 else ""
    mktcap_b    = data["market_cap"] / 1e12

    msg = (
        f"Microsoft MSFT — Full Summary\n"
        f"{data['timestamp']}\n\n"
        f"--- PRICE ---\n"
        f"Current:    ${data['current_price']:.2f}\n"
        f"Change:     {sign_change}{data['change_pct']:.2f}%\n"
        f"Day Range:  ${data['day_low']:.2f} - ${data['day_high']:.2f}\n\n"
        f"--- MARKET ---\n"
        f"Market Cap: ${mktcap_b:.2f}T\n"
        f"Volume:     {data['volume']:,} shares\n\n"
        f"--- 52-WEEK ---\n"
        f"High:       ${data['week_52_high']:.2f}\n"
        f"Low:        ${data['week_52_low']:.2f}\n"
        f"From ATH:   {sign_ath}{data['from_ath']:.1f}%\n\n"
        f"--- MOVING AVERAGES ---\n"
        f"MA50:       ${data['ma50']:.2f}\n"
        f"MA200:      ${data['ma200']:.2f}\n"
        f"vs MA50:    {'ABOVE' if data['current_price'] > data['ma50'] else 'BELOW'}\n"
        f"vs MA200:   {'ABOVE' if data['current_price'] > data['ma200'] else 'BELOW'}\n\n"
        f"--- HISTORICAL ---\n"
        f"IPO (1986): $0.09\n"
        f"From IPO:   +{data['from_ipo']:,.0f}%\n"
        f"All Time High: $467.56 (Jul 2024)"
    )
    await update.message.reply_text(msg)

# ── COMANDO: /signal ──────────────────────────────────────────
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Analyzing trading signals...")
    data = get_msft_data()
    if not data:
        await update.message.reply_text("Error fetching data. Please try again.")
        return

    signal_name, signal_desc = get_signal(data)

    msg = (
        f"MSFT Trading Signal\n"
        f"{data['timestamp']}\n\n"
        f"Signal: {signal_name}\n"
        f"{signal_desc}\n\n"
        f"Current Price: ${data['current_price']:.2f}\n"
        f"MA50:          ${data['ma50']:.2f}\n"
        f"MA200:         ${data['ma200']:.2f}\n\n"
        f"Price vs MA50:  {'ABOVE' if data['current_price'] > data['ma50'] else 'BELOW'} "
        f"by ${abs(data['current_price'] - data['ma50']):.2f}\n"
        f"Price vs MA200: {'ABOVE' if data['current_price'] > data['ma200'] else 'BELOW'} "
        f"by ${abs(data['current_price'] - data['ma200']):.2f}\n\n"
        f"Note: This is informational only, not financial advice."
    )
    await update.message.reply_text(msg)

# ── COMANDO: /history ─────────────────────────────────────────
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"Microsoft MSFT — Key Historical Facts\n\n"
        f"1986  IPO at $0.09 per share\n"
        f"1990  Windows 3.0 launched\n"
        f"1995  Windows 95 — stock explodes\n"
        f"1999  Peak $59.56 — dot-com bubble\n"
        f"2000  Crash begins — lost decade starts\n"
        f"2009  Bottom at $15.15\n"
        f"2014  Satya Nadella becomes CEO\n"
        f"2016  Azure becomes market leader\n"
        f"2018  $1 Trillion valuation\n"
        f"2023  OpenAI $10B investment\n"
        f"2024  All Time High $467.56\n\n"
        f"Total Return IPO to today: +422,000%\n"
        f"$1,000 invested in 1986 = $4.2M today\n"
        f"Satya Nadella impact: +1,194% since 2013"
    )
    await update.message.reply_text(msg)

# ── COMANDO: /help ────────────────────────────────────────────
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"MSFT Intelligence Bot — Commands\n\n"
        f"/price   — Live price + daily change\n"
        f"/summary — Complete market summary\n"
        f"/signal  — MA-based trading signal\n"
        f"/history — Key historical milestones\n"
        f"/help    — This menu\n\n"
        f"You can also ask in plain text:\n"
        f"'What is the price of Microsoft?'\n"
        f"'What is the 52-week high?'\n"
        f"'Is MSFT above the 200-day average?'"
    )
    await update.message.reply_text(msg)

# ── MENSAJES DE TEXTO LIBRE ───────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde preguntas en lenguaje natural."""
    text = update.message.text.lower()

    price_keywords   = ["price","precio","vale","cost","worth","cuanto","how much","value","trading"]
    summary_keywords = ["summary","resumen","full","completo","all","todo","detail"]
    signal_keywords  = ["signal","señal","buy","sell","comprar","vender","trend","tendencia"]
    history_keywords = ["history","historia","historical","ipo","1986","nadella","mileston"]
    high_keywords    = ["52","week","high","alto","maximo","maximum","highest"]
    low_keywords     = ["low","bajo","minimo","minimum","lowest","bottom"]
    ma_keywords      = ["average","promedio","ma50","ma200","moving","200","50"]
    cap_keywords     = ["market cap","capitalizacion","cap","trillion","billion"]

    data = None

    if any(k in text for k in price_keywords):
        data = get_msft_data()
        if data:
            sign = "+" if data["change"] >= 0 else ""
            arrow = "UP" if data["change"] >= 0 else "DOWN"
            msg = (
                f"Microsoft (MSFT) right now:\n\n"
                f"Price:  ${data['current_price']:.2f}  {arrow}\n"
                f"Change: {sign}${data['change']:.2f} ({sign}{data['change_pct']:.2f}%)\n"
                f"As of:  {data['timestamp']}"
            )
        else:
            msg = "Could not fetch price. Please try again."

    elif any(k in text for k in high_keywords):
        data = get_msft_data()
        if data:
            msg = (
                f"MSFT 52-Week Range:\n\n"
                f"High: ${data['week_52_high']:.2f}\n"
                f"Low:  ${data['week_52_low']:.2f}\n"
                f"Now:  ${data['current_price']:.2f}"
            )
        else:
            msg = "Could not fetch data. Please try again."

    elif any(k in text for k in low_keywords):
        data = get_msft_data()
        if data:
            msg = (
                f"MSFT 52-Week Low:\n\n"
                f"Low:  ${data['week_52_low']:.2f}\n"
                f"High: ${data['week_52_high']:.2f}\n"
                f"Now:  ${data['current_price']:.2f}"
            )
        else:
            msg = "Could not fetch data. Please try again."

    elif any(k in text for k in ma_keywords):
        data = get_msft_data()
        if data:
            msg = (
                f"MSFT Moving Averages:\n\n"
                f"Current: ${data['current_price']:.2f}\n"
                f"MA50:    ${data['ma50']:.2f} — "
                f"{'ABOVE' if data['current_price'] > data['ma50'] else 'BELOW'}\n"
                f"MA200:   ${data['ma200']:.2f} — "
                f"{'ABOVE' if data['current_price'] > data['ma200'] else 'BELOW'}"
            )
        else:
            msg = "Could not fetch data. Please try again."

    elif any(k in text for k in cap_keywords):
        data = get_msft_data()
        if data:
            mktcap_t = data["market_cap"] / 1e12
            msg = f"MSFT Market Cap: ${mktcap_t:.2f} Trillion"
        else:
            msg = "Could not fetch data. Please try again."

    elif any(k in text for k in signal_keywords):
        data = get_msft_data()
        if data:
            sig, desc = get_signal(data)
            msg = f"MSFT Signal: {sig}\n{desc}"
        else:
            msg = "Could not fetch data. Please try again."

    elif any(k in text for k in history_keywords):
        msg = (
            f"MSFT Key Milestones:\n\n"
            f"1986 IPO: $0.09\n"
            f"1999 Peak: $59.56\n"
            f"2009 Bottom: $15.15\n"
            f"2014 Satya Nadella CEO\n"
            f"2024 ATH: $467.56\n"
            f"Total Return: +422,000%"
        )

    elif any(k in text for k in summary_keywords):
        data = get_msft_data()
        if data:
            sign = "+" if data["change"] >= 0 else ""
            mktcap_t = data["market_cap"] / 1e12
            msg = (
                f"MSFT Full Summary:\n\n"
                f"Price:  ${data['current_price']:.2f}\n"
                f"Change: {sign}{data['change_pct']:.2f}%\n"
                f"Cap:    ${mktcap_t:.2f}T\n"
                f"MA50:   ${data['ma50']:.2f}\n"
                f"MA200:  ${data['ma200']:.2f}\n"
                f"52W Hi: ${data['week_52_high']:.2f}\n"
                f"52W Lo: ${data['week_52_low']:.2f}"
            )
        else:
            msg = "Could not fetch data. Please try again."

    else:
        msg = (
            f"I can answer questions about Microsoft (MSFT).\n\n"
            f"Try asking:\n"
            f"- What is the price of Microsoft today?\n"
            f"- What is the 52-week high?\n"
            f"- Is MSFT above the 200-day average?\n"
            f"- What is the market cap?\n\n"
            f"Or use commands: /price /summary /signal /history"
        )

    await update.message.reply_text(msg)

# ── MAIN ──────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("   MSFT Intelligence Bot — Starting...")
    print("=" * 55)
    print(f"   Token:   {TOKEN[:20]}...")
    print(f"   Chat ID: {CHAT_ID}")
    print(f"   Ticker:  {TICKER}")
    print("=" * 55)
    print("\nBot is running. Open Telegram and talk to your bot.")
    print("Press Ctrl+C to stop.\n")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("price",   price))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("signal",  signal))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("help",    help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
