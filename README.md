# Okto Advisor Bot - Telegram Bot

Okto Advisor Bot is an advanced Telegram bot designed to assist users in the world of decentralized finance (DeFi). The bot provides various features such as market insights, portfolio management, social trading, and more.

![image](https://github.com/user-attachments/assets/eec3d00a-8835-4c0b-93c3-9672869211fb)


## Features

1. **📊 Market Insights**: Get real-time alerts for price changes, volume spikes, and other important market indicators.
2. **💰 Portfolio Management**: View and manage your crypto assets, track your trading performance, and make informed decisions.
3. **🤝 Social Trading**: Follow expert traders, copy their trades, and see their strategies to improve your trading performance.
4. **💹 Staking & Yield Farming**: Bots assist with staking, yield farming, and notify users about new opportunities in the DeFi space.
5. **🔗 Help & Support**: Access support and resources to help with any questions or issues regarding the bot or the features.

## Commands

- `/start`: Start the bot and receive a welcome message with available features.
- `/help`: Show the list of available commands and their descriptions.
- `/portfolio`: Get the details of your portfolio.
- `/portfolio_activity`: View the latest activity in your portfolio.
- `/transfer_tokens`: Transfer tokens across different networks.
- `/feedback`: Provide feedback or suggestions for improvement.
- `/search <keyword>`: Search for specific insights or information from the bot.

## Button Menu

Upon starting the bot, users will be presented with an interactive button menu, which includes the following options:

- 📊 *Market Insights*: Receive real-time alerts for market price changes, volume spikes, and other significant events.
- 💰 *Portfolio Management*: View your crypto portfolio, track performance, and manage your assets.
- 🤝 *Social Trading*: Follow expert traders and copy their trades within the Telegram platform.
- 💹 *Staking & Yield Farming*: Get notified about new staking and yield farming opportunities.
- 🔗 *Help & Support*: Access help and additional resources.

## Setup

1. Install the required dependencies:
    ```bash
    pip install python-dotenv
    pip install python-telegram-bot nest_asyncio
    ```

2. Create a `.env` file with your API keys and Telegram token:
    ```
    OKTO_API_KEY=your-okto-api-key
    OKTO_API_BASE=api.okto.com
    TELEGRAM_TOKEN=your-telegram-bot-token
    ```

3. Run the bot:
    ```bash
    python bot.py
    ```

## How It Works

The bot retrieves real-time data from the OKTO API to provide insights on market trends, portfolio performance, staking opportunities, and more. It also integrates with Telegram for social trading and community engagement.

## Contribution

Feel free to fork the repository and submit pull requests for any improvements. Whether it's fixing bugs, adding features, or improving documentation, your contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
