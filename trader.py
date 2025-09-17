# -------------------------------------------------
# Real-Time Coinbase Trading Engine
# -------------------------------------------------
import os
from time import sleep
from dotenv import load_dotenv
from coinbase.rest import RESTClient
from json import dumps
from decimal import Decimal, ROUND_DOWN
from datetime import datetime
from PaperRESTClient import PaperRESTClient 

# Load variables from .env and initialize client
load_dotenv()

api_key = os.getenv("COINBASE_API_KEY")
api_secret = os.getenv("COINBASE_API_SECRET")

# Instructions:
# Get the api keys from Coinbase
# Enable View and Trade permissions 
# Use ECDSA signing algorithm when creating the keys
# Save Keys in .env

# USE PAPER CLIENT FOR PAPER TRADING
client = PaperRESTClient(api_key=api_key, api_secret=api_secret)
# client = RESTClient(api_key=api_key, api_secret=api_secret)

def get_balance(ticker: str, in_usd: bool = True) -> Decimal:
    """
    Get the available balance for a given currency.

    Args:
        ticker (str): Currency symbol (e.g., "BTC").
        in_usd (bool, optional): If True, returns value in USD. 
            If False, returns balance in ticker units. Defaults to True.

    Returns:
        Decimal: Balance in USD (rounded to 2 decimals) or in ticker units.
    """
    accounts = client.get_accounts()
    account = next((acc for acc in accounts["accounts"] if acc["currency"] == ticker), None)
    if account is None:
        return 0
    
    balance = Decimal(account["available_balance"]["value"])
    if not in_usd:
        return balance
    
    price = Decimal(client.get_product(f"{ticker}-USD")["price"])
    value = balance * price
    value = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    return value

def get_by_usd(ticker: str, usd_amount: Decimal) -> Decimal:
    """
    Convert a USD amount into ticker units, rounded down to base_increment.

    Args:
        ticker (str): Currency symbol (e.g., "BTC").
        usd_amount (Decimal): Amount in USD to convert.

    Returns:
        Decimal: Quantity of ticker, rounded to base_increment.
    """
    price = Decimal(client.get_product(f"{ticker}-USD")["price"])
    base_increment = Decimal(client.get_product(f"{ticker}-USD")["base_increment"])

    ticker_qty = Decimal(usd_amount) / price
    ticker_qty = Decimal(ticker_qty).quantize(base_increment, rounding=ROUND_DOWN)
    return ticker_qty

def sell_order(ticker: str, usd_amount: Decimal):
    """
    Place a market sell order for a given USD notional.

    Args:
        ticker (str): Currency symbol (e.g., "BTC").
        usd_amount (Decimal): USD value to sell.
    """
    balance = get_balance(ticker, in_usd=False)
    order_qty = get_by_usd(ticker, usd_amount)
    
    if order_qty > balance:
        print("Insufficient Funds")
        return
    
    order = client.market_order_sell(
        client_order_id=f"sell-{ticker}-{datetime.now().timestamp()}",
        product_id=f"{ticker}-USD",
        base_size=str(order_qty)
    )

    order_id = order["success_response"]["order_id"]

    # Poll until the order reaches a terminal state
    while True:
        status = client.get(f"/api/v3/brokerage/orders/historical/{order_id}")["order"]["status"]
        print("Order status:", status)
        if status in ("FILLED", "CANCELLED", "EXPIRED", "FAILED"):
            return
        sleep(2)

def strategy(ticker: str, principal: Decimal, rake: Decimal = 0.15, delay: int = 30):
    """
    Run a rake strategy on a given ticker.

    The strategy holds a principal USD value of the asset.
    Any balance above (principal + rake) is sold periodically.

    Args:
        ticker (str): Currency symbol (e.g., "BTC").
        principal (Decimal): Principal amount to maintain in USD.
        rake (Decimal, optional): Minimum profit margin above principal to trigger sell. Defaults to 0.15.
        delay (int, optional): Time (seconds) to wait between balance checks. Defaults to 30.
    """
    principal = Decimal(principal)
    rake = Decimal(rake)
    reserve = get_balance(ticker) - principal
    if reserve < 0:
        print(f"Insufficient Funds. Saving until principal of {principal} is met.")
        reserve = 0

    while True:
        timestamp = client.get("/v2/time")["data"]["epoch"]
        print(datetime.fromtimestamp(timestamp))

        # rake strategy
        balance = get_balance(ticker) - reserve
        print("Strategy Balance: ", balance)
        if balance > principal + rake:
            sell_amount = round(balance - principal, 2)
            print("Selling: ", sell_amount)
            sell_order(ticker, sell_amount)
        else:
            print("Holding...")
        sleep(delay)

strategy(ticker="BTC", principal=2000.00, delay=3)