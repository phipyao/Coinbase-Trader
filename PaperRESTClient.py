# -------------------------------------------------
# Paper Client (replaces Coinbase RESTClient for Paper Trading)
# -------------------------------------------------
from datetime import datetime
from decimal import Decimal
from coinbase.rest import RESTClient

class PaperRESTClient:
    def __init__(self, api_key, api_secret, usd_balance=0, btc_balance=1):
        self.real_client = RESTClient(api_key=api_key, api_secret=api_secret)
        self.usd_balance = Decimal(usd_balance)
        self.btc_balance = Decimal(btc_balance)

    def get_accounts(self):
        """Return paper account balance."""
        return {
            "accounts": [
                {
                    "currency": "USD",
                    "available_balance": {"value": str(self.usd_balance), "currency": "USD"}
                },
                {
                    "currency": "BTC",
                    "available_balance": {"value": str(self.btc_balance), "currency": "BTC"}
                }
            ]
        }

    def get_product(self, product_id: str):
        """Use the real API for live price/base_increment data."""
        return self.real_client.get_product(product_id)

    def market_order_sell(self, client_order_id, product_id, base_size):
        """Prevent real sells — simulate instead."""
        print(f"[TEST] Simulated SELL: {base_size} {product_id.split('-')[0]}")
        return {"success_response": {f"order_id": {client_order_id}}}

    def get(self, endpoint: str):
        """Fake order history & time API calls."""
        if "brokerage/orders" in endpoint:
            # Pretend the order always fills
            return {"order": {"status": "FILLED"}}
        elif "/v2/time" in endpoint:
            return {"data": {"epoch": int(datetime.now().timestamp())}}
        return {}