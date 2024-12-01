import logging
import asyncio
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
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
        "Click 'Continue' to explore the features of the bot."
    )

    # Enhanced Button Menu with "Continue"
    keyboard = [
        [InlineKeyboardButton("📊 Market Insights", callback_data="continue_Market Monitoring")],
        [InlineKeyboardButton("💰 Portfolio Management", callback_data="continue_Portfolio Management")],
        [InlineKeyboardButton("🤝 Social Trading", callback_data="continue_Social Trading")],
        [InlineKeyboardButton("💹 Staking & Yield Farming", callback_data="continue_Staking Yield Farming")],
        [InlineKeyboardButton("🔗 Help & Support", callback_data="Help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Callback: Continue Button Handler
async def continue_insight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user clicking 'Continue' for a feature."""
    query = update.callback_query
    insight_key = query.data.split("_", 1)[1]

    if insight_key in INSIGHTS:
        insight_text = INSIGHTS[insight_key]
        await query.answer()
        await query.edit_message_text(
            text=f"📘 *{insight_key}*\n{insight_text}",
            parse_mode="Markdown"
        )

        # Add a "Return to Menu" button after showing the detail
        keyboard = [
            [InlineKeyboardButton("🔙 Return to Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("What would you like to explore next?", reply_markup=reply_markup)

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available commands."""
    await update.message.reply_text(
        "📜 *Available Commands:*\n\n"
        "/start - Welcome message with insights menu.\n"
        "/help - Display this help message.\n"
        "/trade - Execute a sample cryptocurrency trade.\n"
        "/market - Fetch the latest market data summary.\n"
        "/feedback - Share your feedback about this bot.\n"
        "/search <keyword> - Search insights by keyword.\n"
        "/preferences - View or update your saved preferences.\n"
        "/broadcast <message> - (Admin-only) Broadcast a message to all users.",
        parse_mode="Markdown"
    )

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

# Command: Preferences
async def preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage user preferences dynamically."""
    user_id = update.effective_user.id
    user_preferences = USER_PREFERENCES.get(user_id, [])

    if context.args:
        new_preference = " ".join(context.args)
        if new_preference not in user_preferences:
            user_preferences.append(new_preference)
            USER_PREFERENCES[user_id] = user_preferences
            await update.message.reply_text(f"✅ Added '{new_preference}' to your preferences!")
        else:
            await update.message.reply_text(f"⚠️ '{new_preference}' is already in your preferences.")
    else:
        if user_preferences:
            await update.message.reply_text(
                "🌟 *Your Preferences:*\n- " + "\n- ".join(user_preferences), parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "💡 You have no preferences set. Use `/preferences <preference>` to add one."
            )

# Command: Trade
async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute a sample trade with better feedback."""
    trade_details = {"symbol": "BTCUSDT", "quantity": 0.01, "side": "buy"}
    result = execute_trade(OKTO_API_KEY, trade_details)

    if 'error' in result:
        await update.message.reply_text(f"❌ Error executing trade: {result['error']}")
    else:
        TRADE_LOGS.append(result)
        await update.message.reply_text(
            f"✅ *Trade Successful!*\n\n"
            f"🪙 Symbol: {trade_details['symbol']}\n"
            f"🔄 Quantity: {trade_details['quantity']}\n"
            f"📈 Side: {trade_details['side']}\n\n"
            f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )

# Command: Market
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display detailed market data."""
    data = get_market_data(OKTO_API_KEY)
    if 'error' in data:
        await update.message.reply_text(f"❌ Error fetching market data: {data['error']}")
    else:
        summary = (
            f"📊 *Market Data Summary:*\n\n"
            f"📈 BTC/USDT: {data.get('BTCUSDT', {}).get('price', 'N/A')} USD\n"
            f"📉 ETH/USDT: {data.get('ETHUSDT', {}).get('price', 'N/A')} USD\n"
            f"📊 24h Volume: {data.get('volume', 'N/A')} USD"
        )
        await update.message.reply_text(summary)

# Callback for returning to the main menu
async def return_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to the main menu."""
    await start(update, context)

# Main function to start the bot
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("feedback", feedback))
    application.add_handler(CommandHandler("preferences", preferences))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("market", market))
    application.add_handler(CallbackQueryHandler(continue_insight))
    application.add_handler(CallbackQueryHandler(return_to_menu, pattern="^start$"))

    # Run the bot
    await application.run_polling()

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
