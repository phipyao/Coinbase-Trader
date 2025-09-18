# -------------------------------------------------
# Real-Time Coinbase Trading Engine
# -------------------------------------------------
from time import sleep
from decimal import Decimal
from datetime import datetime

from Client import Client

client = Client(paper=True)

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

    reserve = client.get_balance(ticker) - principal
    if reserve < 0:
        print(f"Insufficient Funds. Saving until principal of {principal} is met.")
        reserve = 0

    while True:
        timestamp = client.get("/v2/time")["data"]["epoch"]
        print(datetime.fromtimestamp(timestamp))

        # rake strategy
        balance = client.get_balance(ticker) - reserve
        print("Strategy Balance: ", balance)
        if balance > principal + rake:
            sell_amount = round(balance - principal, 2)
            print("Selling: ", sell_amount)
            client.sell_order(ticker, sell_amount)
        else:
            print("Holding...")
        sleep(delay)

strategy(ticker="BTC", principal=2000.00, delay=3)