
# Coinbase Trading Engine for Python

Crypto Trading Engine using the Coinbase Advanced REST Client.

## Installation

```bash
pip3 install -r requirements.txt
```
## Coinbase Developer Platform (CDP) API Keys

This Trading Engine uses the Cloud Developer Platform (CDP) API keys. To use this program, you will need to create a CDP API key and secret by following the instructions from this [link](https://portal.cdp.coinbase.com/projects/api-keys).
Make sure to save your API key and secret in a safe place. You will not be able to retrieve your secret again.

1. Click "Create API key"
2. Give the API key any nickname
3. Under "API restrictions" -> Enable View and Trade Checkboxes 
4. Under Advanced Settings -> Change Signature algorithm to ECDSA
5. Click "Create"
6. Set your API key and secret in a .env file. For example:
```bash
#.env file
COINBASE_API_KEY="organizations/{org_id}/apiKeys/{key_id}"
COINBASE_API_SECRET="-----BEGIN EC PRIVATE KEY-----\nYOUR PRIVATE KEY\n-----END EC PRIVATE KEY-----\n"
```


WARNING: It is not reccomended that you save your API secrets directly in your code outside of testing purposes. Best practice is to use a secrets manager and access your secrets that way. You should be careful about exposing your secrets publicly if posting code that leverages this library.

## Coinbase Trade Engine Client

In your code, import the Client class and instantiate it:
```python
from CBTradeEngine import Client

client = Client() # uses .env variables for API key and secret
```

If you did not set your API key and secret in your environment, you can pass them in as arguments:
```python
api_key = "organizations/{org_id}/apiKeys/{key_id}"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nYOUR PRIVATE KEY\n-----END EC PRIVATE KEY-----\n"

client = Client(api_key=api_key, api_secret=api_secret)
```

The client also supports paper trading to test strategies
```python
client = Client(paper=True)
```

### Using the REST Client Examples

sell_order: Market sell order for sell_amount of BTC in USD, returns time to complete order
```python
client.sell_order("BTC", sell_amount)
```

buy_order: Market buy order for quote_amount of BTC in USD, returns time to complete order
```python
client.buy_order("BTC", quote_amount)
```

get_balance: Returns Account's balance of an input ticker in USD
```python
client.get_balance(ticker)
```

get_time: Returns current time as a Datetime object
```python
client.get_time()
```

get_account_values: Returns a Dictionary of all ticker balances in USD. "TOTAL" key is included for total value of account.
```python
client.get_account_values()
```