import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API keys
OKTO_API_KEY = 'c6ab43bd-cf0b-4922-9be9-8750e72d223b'
TELEGRAM_TOKEN = '8118102733:AAEL6abhJHS8FYxShRt7NmzBYMuBIBs5cvg'

# Static insights for each category
INSIGHTS = {
    "Automated Trade Execution": "Bots can execute buy/sell orders based on predefined strategies or signals, automating cryptocurrency trading.",
    "Market Monitoring": "Bots provide real-time alerts and updates on market conditions, such as price changes and volume spikes.",
    "Portfolio Management": "Users can track and manage their crypto assets directly through chat interfaces, monitoring trading performance.",
    "Social Trading": "Some bots allow users to follow and copy trades from expert traders, facilitating social trading within the platform.",
    "Staking & Yield Farming": "Bots guide users through staking processes and notify them of new yield farming opportunities.",
    "Loan Management": "Integration with DeFi lending platforms enables users to borrow or lend assets directly from the chat interface.",
    "DeFi Alerts": "Users receive alerts for significant changes in DeFi platforms, such as APY fluctuations or new pool offerings.",
    "Voting & Polls": "Bots manage community governance by organizing votes and polls in DAO communities.",
    "Event Management": "Bots help organize and promote events like AMAs, webinars, or hackathons within chat groups.",
    "Automated Moderation": "Bots enforce moderation policies by managing group rules, filtering out spam, and maintaining a healthy community environment.",
    "Advertising & Partnerships": "Bots can partner with crypto projects or services to promote offerings through sponsored messages."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Welcome to Okto Advisor Bot!\n"
        "Choose a category to get more information:\n"
        "/trade_execution - Automated Trade Execution\n"
        "/market_monitoring - Market Monitoring\n"
        "/portfolio_management - Portfolio Management\n"
        "/social_trading - Social Trading\n"
        "/staking_yield_farming - Staking & Yield Farming\n"
        "/loan_management - Loan Management\n"
        "/defi_alerts - DeFi Alerts\n"
        "/voting_polls - Voting & Polls\n"
        "/event_management - Event Management\n"
        "/automated_moderation - Automated Moderation\n"
        "/advertising_partnerships - Advertising & Partnerships"
    )
    await update.message.reply_text(message)

async def send_insight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text[1:]  # Remove the leading '/'
    insight_key = command.replace('_', ' ').title()
    
    if insight_key in INSIGHTS:
        await update.message.reply_text(INSIGHTS[insight_key])
    else:
        await update.message.reply_text("Sorry, I don't have information on that topic.")

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
        logger.error(f"Error executing trade: {e}")
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
        logger.error(f"Error fetching market data: {e}")
        return {"error": str(e)}

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = get_market_data(OKTO_API_KEY)
    if 'error' in data:
        await update.message.reply_text(f"Error fetching market data: {data['error']}")
    else:
        await update.message.reply_text(f'Market Data: {data}')

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    
    # Add handlers for each insight category
    for command in INSIGHTS.keys():
        application.add_handler(CommandHandler(command.lower().replace(' ', '_'), send_insight))

    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("market", market))

    application.run_polling()

if __name__ == '__main__':
    main()
