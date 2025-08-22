
import websocket
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()


DERIV_APP_ID = os.getenv('DERIV_APP_ID')
DERIV_API_URL = f'wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}'

class DerivBot:
    def get_contract_offers(self, symbol):
        offers_req = json.dumps({
            "contracts_for": symbol
        })
        self.ws.send(offers_req)
        response = self.ws.recv()
        print("Contract offerings response:", response)
        return json.loads(response)

    def find_1min_binary_asset(self, asset_list):
        # Try to find an asset with min_contract_duration == '60s' or '1m'
        for asset in asset_list:
            min_dur = asset.get('min_contract_duration', '')
            if min_dur in ['60s', '1m']:
                print(f"Found 1-min asset: {asset['underlying_symbol']} type: {asset['contract_type']}")
                return asset['underlying_symbol'], asset['contract_type']
        print("No 1-min binary asset found.")
        return None, None
    def get_contract_offers(self, symbol):
        offers_req = json.dumps({
            "contracts_for": symbol
        })
        self.ws.send(offers_req)
        response = self.ws.recv()
        print("Contract offerings response:", response)
        return json.loads(response)
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.running = False

    def connect(self):
        try:
            print(f"Connecting to {DERIV_API_URL}...")
            self.ws = websocket.create_connection(DERIV_API_URL)
            print("Connection successful.")
            self.authorize()
            self.running = True
        except Exception as e:
            print(f"Failed to connect to {DERIV_API_URL}")
            print(f"Error: {e}")
            print("Check your internet connection, firewall, and proxy settings.")
            self.ws = None
            self.running = False

    def authorize(self):
        auth_req = json.dumps({
            "authorize": self.api_token
        })
        self.ws.send(auth_req)
        response = self.ws.recv()
        print("Authorization response:", response)

    def get_tick(self, symbol):
        tick_req = json.dumps({
            "ticks": symbol
        })
        self.ws.send(tick_req)
        response = self.ws.recv()
        print("Tick response:", response)
        return json.loads(response)

    def buy_contract(self, symbol, amount, duration, contract_type, duration_unit="m", max_retries=2):
        params = {
            "amount": amount,
            "contract_type": contract_type,
            "currency": "USD",
            "duration": duration,
            "duration_unit": duration_unit,
            "symbol": symbol
        }
        if contract_type in ["CALL", "PUT", "CALLE", "PUTE"]:
            params["basis"] = "stake"
        if contract_type in ["LBFLOATCALL", "LBFLOATPUT", "LBHIGHLOW"]:
            params["multiplier"] = 1
        for attempt in range(max_retries):
            buy_req = json.dumps({
                "buy": 1,
                "price": amount,
                "parameters": params
            })
            self.ws.send(buy_req)
            response = self.ws.recv()
            print(f"Buy response (attempt {attempt+1}):", response)
            resp_json = json.loads(response)
            error = resp_json.get("error", {})
            if error.get("code") == "PriceMoved":
                # Extract new price from error message
                import re
                match = re.search(r"to ([\d\.]+) USD", error.get("message", ""))
                if match:
                    new_price = float(match.group(1))
                    print(f"Retrying with new price: {new_price}")
                    amount = new_price
                    continue
            break
        return resp_json

    def close(self):
        if self.ws:
            self.ws.close()
        self.running = False

    def is_running(self):
        return self.running

    def run_strategy(self, symbol="R_100", amount=1, duration=1):
        if not self.ws:
            self.connect()
        if self.ws:
            offers = self.get_contract_offers(symbol)
            available = offers.get('contracts_for', {}).get('available', [])
            asset_symbol, contract_type = self.find_1min_binary_asset(available)
            if asset_symbol and contract_type:
                self.get_tick(asset_symbol)
                result = self.buy_contract(asset_symbol, amount, duration, contract_type, duration_unit="m")
                return result
            else:
                print("No valid 1-min contract found for binary asset.")
                return {"error": "No valid 1-min contract found."}
        else:
            print("Bot could not connect. Exiting.")
            return {"error": "Connection failed."}


# Singleton bot instance for backend integration
bot_instance = None
def get_bot():
    global bot_instance
    if bot_instance is None:
        API_TOKEN = os.getenv('API_TOKEN')
        bot_instance = DerivBot(API_TOKEN)
    return bot_instance
