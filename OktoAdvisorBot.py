import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
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

# Static insights for each category (expanded)
INSIGHTS = {
    "Automated Trade Execution": "Bots automate buy/sell orders based on predefined strategies, eliminating emotional trading and allowing 24/7 operation.",
    "Market Monitoring": "Real-time alerts on price changes, volume spikes, and market trends. Bots can also scan news and social media for insights.",
    "Portfolio Management": "Monitor your assets, track performance, and receive rebalancing suggestions for better diversification.",
    "Social Trading": "Copy trades from expert traders, follow their strategies, and gain insights through leaderboards and analytics.",
    "Staking Yield Farming": "Simplifies staking and yield farming processes while notifying users about new opportunities and APY updates.",
    "Loan Management": "Monitor DeFi loans, adjust collateral, and receive risk alerts to prevent liquidation directly from the chat.",
    "DeFi Alerts": "Get notified of APY changes, new pools, and major platform updates to optimize your yield farming and staking strategies.",
    "Voting Polls": "Participate in DAO governance easily with real-time vote summaries and results.",
    "Event Management": "Organize AMAs, webinars, or hackathons with scheduling and notification tools integrated into chat groups.",
    "Automated Moderation": "Maintain healthy communities with spam filters, toxic language detection, and rule enforcement.",
    "Advertising Partnerships": "Promote projects with tailored sponsored messages to engage relevant audiences effectively."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command to welcome the user and display categories."""
    keyboard = [[InlineKeyboardButton(key, callback_data=key)] for key in INSIGHTS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to the Okto Advisor Bot! Explore various features and insights:\n\n"
        "1️⃣ Use /help to view all available commands.\n"
        "2️⃣ Select a category below to learn more:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available commands."""
    await update.message.reply_text(
        "/start - Welcome message with insights menu.\n"
        "/trade - Execute a sample cryptocurrency trade.\n"
        "/market - Fetch the latest market data summary.\n"
        "/help - Display this help message."
    )

async def send_insight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send detailed insight for the selected category."""
    query = update.callback_query
    await query.answer()
    
    insight_key = query.data
    if insight_key in INSIGHTS:
        await query.edit_message_text(f"📘 *{insight_key}*\n\n{INSIGHTS[insight_key]}", parse_mode="Markdown")
    else:
        await query.edit_message_text("❌ Sorry, I don't have information on that topic.")

def execute_trade(api_key, trade_details):
    """Execute a trade via API."""
    url = "https://api.okto.tech/trade"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=trade_details)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error executing trade: {e}")
        return {"error": str(e)}

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute a sample trade."""
    trade_details = {"symbol": "BTCUSDT", "quantity": 0.01, "side": "buy"}
    result = execute_trade(OKTO_API_KEY, trade_details)
    if 'error' in result:
        await update.message.reply_text(f"❌ Error executing trade: {result['error']}")
    else:
        await update.message.reply_text(f"✅ Trade executed successfully!\nDetails: {result}")

def get_market_data(api_key):
    """Fetch market data via API."""
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
    """Fetch and display market data."""
    data = get_market_data(OKTO_API_KEY)
    if 'error' in data:
        await update.message.reply_text(f"❌ Error fetching market data: {data['error']}")
    else:
        # Extract and summarize key market metrics
        summary = (
            f"📊 *Market Data Summary:*\n\n"
            f"BTC/USDT Price: {data.get('BTCUSDT', {}).get('price', 'N/A')}\n"
            f"ETH/USDT Price: {data.get('ETHUSDT', {}).get('price', 'N/A')}\n"
            f"Top Gainers: {', '.join(data.get('top_gainers', [])[:3])}\n"
            f"Top Losers: {', '.join(data.get('top_losers', [])[:3])}\n"
        )
        await update.message.reply_text(summary, parse_mode="Markdown")

def main():
    """Run the bot."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(send_insight))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("market", market))

    application.run_polling()

if __name__ == '__main__':
    main()
