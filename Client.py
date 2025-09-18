# -------------------------------------------------
# Trading Engine Built with Coinbase RESTClient and Custom Paper Trading Client
# -------------------------------------------------

import os
from time import sleep
from dotenv import load_dotenv
from coinbase.rest import RESTClient
from json import dumps
from decimal import Decimal, ROUND_DOWN
from datetime import datetime
from PaperRESTClient import PaperRESTClient 

class Client:
    def __init__(self, api_key: str = "", api_secret: str = "", key_file:str = "cdp_api_key.json", paper: bool = False, usd_balance=0, btc_balance=1):
        self.api_key = api_key
        self.api_secret = api_secret

        if load_dotenv():
            # Instructions:
            # Get the api keys from Coinbase
            # Enable View and Trade permissions 
            # Use ECDSA signing algorithm when creating the keys
            # Save Keys in .env
            api_key = os.getenv("COINBASE_API_KEY")
            api_secret = os.getenv("COINBASE_API_SECRET")

        if paper:
            self.client = PaperRESTClient(api_key=api_key, api_secret=api_secret, usd_balance=usd_balance, btc_balance=btc_balance)
        else:
            self.client = RESTClient(api_key=api_key, api_secret=api_secret)

    def get(self, args):
        return self.client.get(args)
    
    def get_balance(self, ticker: str, in_usd: bool = True) -> Decimal:
        """
        Get the available balance for a given currency.

        Args:
            ticker (str): Currency symbol (e.g., "BTC").
            in_usd (bool, optional): If True, returns value in USD. 
                If False, returns balance in ticker units. Defaults to True.

        Returns:
            Decimal: Balance in USD (rounded to 2 decimals) or in ticker units.
        """
        accounts = self.client.get_accounts()
        account = next((acc for acc in accounts["accounts"] if acc["currency"] == ticker), None)
        if account is None:
            return 0
        
        balance = Decimal(account["available_balance"]["value"])
        if not in_usd:
            return balance
        
        price = Decimal(self.client.get_product(f"{ticker}-USD")["price"])
        value = balance * price
        value = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        return value

    def get_by_usd(self, ticker: str, usd_amount: Decimal) -> Decimal:
        """
        Convert a USD amount into ticker units, rounded down to base_increment.

        Args:
            ticker (str): Currency symbol (e.g., "BTC").
            usd_amount (Decimal): Amount in USD to convert.

        Returns:
            Decimal: Quantity of ticker, rounded to base_increment.
        """
        price = Decimal(self.client.get_product(f"{ticker}-USD")["price"])
        base_increment = Decimal(self.client.get_product(f"{ticker}-USD")["base_increment"])

        ticker_qty = Decimal(usd_amount) / price
        ticker_qty = Decimal(ticker_qty).quantize(base_increment, rounding=ROUND_DOWN)
        return ticker_qty

    def sell_order(self, ticker: str, usd_amount: Decimal):
        """
        Place a market sell order for a given USD notional.

        Args:
            ticker (str): Currency symbol (e.g., "BTC").
            usd_amount (Decimal): USD value to sell.
        """
        balance = self.get_balance(ticker, in_usd=False)
        order_qty = self.get_by_usd(ticker, usd_amount)
        
        if order_qty > balance:
            print("Insufficient Funds")
            return
        
        order = self.client.market_order_sell(
            client_order_id=f"sell-{ticker}-{datetime.now().timestamp()}",
            product_id=f"{ticker}-USD",
            base_size=str(order_qty)
        )

        order_id = order["success_response"]["order_id"]

        # Poll until the order reaches a terminal state
        while True:
            status = self.client.get(f"/api/v3/brokerage/orders/historical/{order_id}")["order"]["status"]
            print("Order status:", status)
            if status in ("FILLED", "CANCELLED", "EXPIRED", "FAILED"):
                return
            sleep(2)

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