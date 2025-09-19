# -------------------------------------------------
# Paper Client (replaces Coinbase RESTClient for Paper Trading)
# currently only supports BTC to USD
# does not yet implement fees
# -------------------------------------------------
from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from coinbase.rest import RESTClient

class PaperRESTClient:
    def __init__(self, api_key, api_secret, usd_balance, btc_balance):
        self.real_client = RESTClient(api_key=api_key, api_secret=api_secret)
        self.usd_balance = Decimal(usd_balance)
        self.btc_balance = Decimal(btc_balance).quantize(Decimal("0.00000001"))

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
    
    def market_order_buy(self, client_order_id, product_id, quote_size):
        """
        Simulate a market buy order using USD as the quote size.
        Deduct USD and credit BTC at current market price.
        """
        base_currency, quote_currency = product_id.split("-")
        quote_size = Decimal(quote_size)

        # Make sure the account has enough USD
        if quote_currency == "USD" and quote_size > self.usd_balance:
            raise ValueError("Insufficient USD balance for buy")

        # Get current BTC price in USD
        product = self.get_product(product_id)
        price = Decimal(product["price"])  # USD per BTC

        # Calculate how much BTC we can buy
        base_size = Decimal(quote_size / price)

        # Adjust balances
        self.usd_balance -= Decimal(quote_size).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        self.btc_balance += Decimal(base_size).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)

        return {
            "success": True,
            "success_response": {
                "order_id": client_order_id,
                "filled_size": str(base_size),
                "price": str(price),
                "usd_spent": str(quote_size)
            }
        }

    def market_order_sell(self, client_order_id, product_id, base_size):
        """
        Simulate a market sell order.
        Deduct BTC and credit USD at current market price.
        """
        base_currency, quote_currency = product_id.split("-")
        base_size = Decimal(base_size)

        # Make sure the account has enough BTC
        if base_currency == "BTC" and base_size > self.btc_balance:
            raise ValueError("Insufficient BTC balance for sell")

        # Get current BTC price in USD
        product = self.get_product(product_id)
        price = Decimal(product["price"])  # USD per BTC

        # Adjust balances
        self.btc_balance -= base_size
        usd_gain = base_size * price
        self.usd_balance += Decimal(usd_gain).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        return {
            "success": True,
            "success_response": {
                "order_id": client_order_id,
                "filled_size": str(base_size),
                "price": str(price),
                "usd_gain": str(usd_gain)
            }
        }

    def get(self, endpoint: str):
        """Fake order history & time API calls."""
        if "brokerage/orders" in endpoint:
            # Pretend the order always fills
            return {"order": {"status": "FILLED"}}
        elif "/v2/time" in endpoint:
            return {"data": {"epoch": int(datetime.now().timestamp())}}
        return {}
    
    def get_account_value(self):
        net_worth = Decimal("0.00")
        accounts = self.client.get_accounts()["accounts"]
        for account in accounts:
            balance = Decimal(account["available_balance"]["value"])
            ticker = account["currency"]
            value = Decimal("0.00")
            if ticker == "USD" or ticker == "USDC":
                value = Decimal(balance).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            else:
                price = Decimal(self.client.get_product(f"{ticker}-USD")["price"])
                value = balance * price
                value = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            
            net_worth += value
            # print(f"{ticker}: {value}")
        return net_worth