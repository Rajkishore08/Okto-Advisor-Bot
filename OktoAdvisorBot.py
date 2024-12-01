import logging
import asyncio
import http.client
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API keys and base URL
OKTO_API_KEY = 'c6ab43bd-cf0b-4922-9be9-8750e72d223b'
OKTO_API_BASE = 'api.okto.com'
TELEGRAM_TOKEN = '8118102733:AAEL6abhJHS8FYxShRt7NmzBYMuBIBs5cvg'

# Static insights for each category
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

# Memory to store user preferences
USER_PREFERENCES = {}
TRADE_LOGS = []  # To store trade logs for review

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command with dynamic greeting and enhanced menu."""
    user = update.effective_user
    current_hour = datetime.now().hour

    # Dynamic Greeting
    if 5 <= current_hour < 12:
        greeting = "☀️ Good Morning"
    elif 12 <= current_hour < 18:
        greeting = "🌤️ Good Afternoon"
    else:
        greeting = "🌙 Good Evening"

    # Welcome Message
    welcome_message = (
        f"{greeting}, {user.first_name}!\n\n"
        "🤖 *Welcome to Okto Advisor Bot* – Your assistant for DeFi insights.\n"
        "Select a feature below to explore!"
    )

    # Enhanced Button Menu
    keyboard = [
        [InlineKeyboardButton("📊 Market Insights", callback_data="Market Monitoring")],
        [InlineKeyboardButton("💰 Portfolio Management", callback_data="Portfolio Management")],
        [InlineKeyboardButton("🤝 Social Trading", callback_data="Social Trading")],
        [InlineKeyboardButton("💹 Staking & Yield Farming", callback_data="Staking Yield Farming")],
        [InlineKeyboardButton("🔗 Help & Support", callback_data="Help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available commands."""
    await update.message.reply_text(
        "📜 *Available Commands:*\n\n"
        "/start - Welcome message with insights menu.\n"
        "/help - Display this help message.\n"
        "/trade - Execute a sample cryptocurrency trade.\n"
        "/market - Fetch the latest market data summary.\n"
        "/portfolio - Fetch your portfolio details.\n"
        "/portfolio_activity - Fetch your portfolio activity.\n"
        "/transfer_tokens - Execute a token transfer.\n"
        "/feedback - Share your feedback about this bot.\n"
        "/search <keyword> - Search insights by keyword.\n"
        "/preferences - View or update your saved preferences.\n"
        "/broadcast <message> - (Admin-only) Broadcast a message to all users.",
        parse_mode="Markdown"
    )

# Command: Fetch Portfolio Details
async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch portfolio details from OKTO API."""
    portfolio_data = get_portfolio()

    if 'error' in portfolio_data:
        await update.message.reply_text(f"❌ Error fetching portfolio data: {portfolio_data['error']}")
    else:
        await update.message.reply_text(f"📊 *Your Portfolio Details:* \n\n{portfolio_data}", parse_mode="Markdown")

# Command: Fetch Portfolio Activity
async def portfolio_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch portfolio activity from OKTO API."""
    activity_data = get_portfolio_activity()

    if 'error' in activity_data:
        await update.message.reply_text(f"❌ Error fetching portfolio activity: {activity_data['error']}")
    else:
        await update.message.reply_text(f"📈 *Your Portfolio Activity:* \n\n{activity_data}", parse_mode="Markdown")

# Command: Transfer Tokens
async def transfer_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute token transfer using OKTO API."""
    if len(context.args) < 4:
        await update.message.reply_text("❌ Please provide the required arguments: /transfer_tokens <network_name> <token_address> <quantity> <recipient_address>")
        return

    network_name = context.args[0]
    token_address = context.args[1]
    quantity = context.args[2]
    recipient_address = context.args[3]

    transfer_response = transfer_tokens(network_name, token_address, quantity, recipient_address)

    if 'error' in transfer_response:
        await update.message.reply_text(f"❌ Error transferring tokens: {transfer_response['error']}")
    else:
        await update.message.reply_text(f"✅ Token transfer successful: {transfer_response}", parse_mode="Markdown")

# Command: Search Insights
async def search_insights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search insights by keyword."""
    if not context.args:
        await update.message.reply_text("❓ Please provide a keyword to search. Usage: `/search <keyword>`")
        return

    keyword = " ".join(context.args).lower()
    results = {key: val for key, val in INSIGHTS.items() if keyword in key.lower() or keyword in val.lower()}

    if results:
        response = "\n\n".join([f"📘 *{key}*\n{val}" for key, val in results.items()])
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No insights found for the given keyword.")

# Feedback Collection
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Collect user feedback with optional admin logging."""
    feedback_message = " ".join(context.args) if context.args else None
    user = update.effective_user

    if feedback_message:
        # Log feedback for admin review
        logger.info(f"Feedback from {user.first_name} ({user.id}): {feedback_message}")
        await update.message.reply_text(
            "🙏 Thank you for your feedback! We value your input and will use it to improve the bot."
        )
    else:
        await update.message.reply_text(
            "💡 Please provide your feedback using `/feedback <your message>`."
        )

# Main Function: Running the Bot
async def main() -> None:
    """Start the bot."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("portfolio_activity", portfolio_activity))
    app.add_handler(CommandHandler("transfer_tokens", transfer_tokens))
    app.add_handler(CommandHandler("search", search_insights))
    app.add_handler(CommandHandler("feedback", feedback))

    # Run the bot until Ctrl+C is pressed
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

# Function to fetch portfolio activity from OKTO API
def get_portfolio_activity():
    """Fetch portfolio activity from OKTO API."""
    conn = http.client.HTTPSConnection(OKTO_API_BASE)
    headers = { 'Authorization': f"Bearer {OKTO_API_KEY}" }
    
    conn.request("GET", "/api/v1/portfolio/activity", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return data.decode("utf-8")

# Function to fetch portfolio details from OKTO API
def get_portfolio():
    """Fetch portfolio balance details from OKTO API."""
    conn = http.client.HTTPSConnection(OKTO_API_BASE)
    headers = { 'Authorization': f"Bearer {OKTO_API_KEY}" }
    
    conn.request("GET", "/api/v1/portfolio", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return data.decode("utf-8")

# Function to execute token transfer on OKTO API
def transfer_tokens(network_name, token_address, quantity, recipient_address):
    """Execute a token transfer using OKTO API."""
    conn = http.client.HTTPSConnection(OKTO_API_BASE)
    
    payload = json.dumps({
        "network_name": network_name,
        "token_address": token_address,
        "quantity": quantity,
        "recipient_address": recipient_address
    })
    
    headers = {
        'Authorization': f"Bearer {OKTO_API_KEY}",
        'Content-Type': "application/json"
    }
    
    conn.request("POST", "/api/v1/transfer/tokens/execute", payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return data.decode("utf-8")

