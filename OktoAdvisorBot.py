import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# API keys
OKTO_API_KEY = 'c6ab43bd-cf0b-4922-9be9-8750e72d223b'
TELEGRAM_TOKEN = '8118102733:AAEL6abhJHS8FYxShRt7NmzBYMuBIBs5cvg'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome to Okto Advisor Bot!')

def execute_trade(api_key, trade_details):
    url = "https://api.okto.tech/trade"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json=trade_details)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trade_details = {
        "symbol": "BTCUSDT",
        "quantity": 0.01,
        "side": "buy"
    }
    result = execute_trade(OKTO_API_KEY, trade_details)
    if 'error' in result:
        await update.message.reply_text(f"Error executing trade: {result['error']}")
    else:
        await update.message.reply_text(f'Trade executed: {result}')

def get_market_data(api_key):
    url = "https://api.okto.tech/market-data"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = get_market_data(OKTO_API_KEY)
    if 'error' in data:
        await update.message.reply_text(f"Error fetching market data: {data['error']}")
    else:
        await update.message.reply_text(f'Market Data: {data}')

def main():
    # Use ApplicationBuilder instead of Updater
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("market", market))

    # Start the bot using run_polling() directly without asyncio.run()
    application.run_polling()

if __name__ == '__main__':
    main()
