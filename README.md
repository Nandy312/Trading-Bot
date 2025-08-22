# Trading-Bot
# Binary Trading Bot (Deriv)

This project is a template for a binary options trading bot using the Deriv API.

## Setup

1. Install Python 3.8+
2. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
3. Get your Deriv API token and App ID from https://deriv.com
4. Edit `src/bot.py` and add your API token and App ID.

## Usage

Run the bot:
```bash
python src/bot.py
```

## Features
- Connects to Deriv via WebSocket
- Authorizes and places trades
- Simple example strategy (can be extended)

## Next Steps
- Implement your trading strategy logic
- Add risk management
- Backtest and optimize
