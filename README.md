# TradeX SDK (Python) 🐍

Welcome to the official Python SDK for TradeX – a simple and powerful trading API integration.

---

## 📦 Installation Guide

Follow the steps below to set up and start using the TradeX SDK:

### ✅ Step 1: Create a Project Folder

Create a folder for your project and navigate into it.

```bash
mkdir TradeX
cd TradeX
```

### ✅ Step 2: Set Up Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

### ✅ Step 3: Activate the Virtual Environment

#### On **Windows**

```bash
venv\Scripts\activate
```

#### On **macOS / Linux**

```bash
source venv/bin/activate
```

### ✅ Step 4: Install the SDK Dependencies

> 📁 **Download the `dependencies.whl` file from our GitHub repository.** This file is required before proceeding.

```bash
pip install dist/dependencies.whl
```

### 🔁 Optional: Reinstall SDK dependencies if updates are made

```bash
pip install dist/dependencies.whl --force-reinstall
```

---

## 🚀 Usage Example

Create a `main.py` file with the following code to get started:

```python
import json

from tradex_client import TradeXClient
from tradex_client.exceptions import *
from tradex_client.models import *

# All user credentials and authentication info are saved in a .env file on first run. No need to pass them again manually. Only have to pass app key and secret key every time as it is not saved in env

client = TradeXClient(
    app_key="your_app_key",
    secret_key="your_secret_key",
    base_url="https://your_domain.com:port",
    client_id="ABC123",
    user_id="ABC123"
)

# Login
response = client.login(get_new_token=True)
print("Login Response")
print(json.dumps(response.get_dict(), indent=2))

# Place New Order
new_order_details = NewOrderRequest(
    exchange="BseFO",
    code="861380",
    side="Buy",
    quantity=30,
    price=63000,
    book="RL",
    trigger_price=0,
    disclosed_qty=0,
    product="Normal",
    validity="Day",
    gtd="",
    order_flag=0,
    sender_order_no=1517,
    algol_id=0,
)

response = client.place_new_order(new_order_details)
print("New Order Response")
print(json.dumps(response.get_dict(), indent=2))

# Logout
response = client.logout()
print("Logout Response")
print(json.dumps(response, indent=2))
```

---

## 📁 WebSocket Callbacks

```
self.client.register_callback("order", self.handle_order_event)
self.client.register_callback("trade", self.handle_trade_event)

def handle_trade_event(self, data: TradesBookData):
        print("Trade Event Received")
        print(f"Symbol        : {data.symbol}")
        print(f"Client        : {data.client}")
        print(f"Trade Side    : {data.side}")
        print(f"Traded Qty    : {data.traded_qty}")
        print(f"Traded Price  : {data.traded_price}")
        print(f"Trade Value   : {data.traded_value}")
        print(f"Trade Time    : {data.trade_time}")
        print(f"Order Status  : {data.order_status}")
        print(f"Exchange Order No: {data.exchange_order_no}")
        print("-" * 40)

    def handle_order_event(self, data: OrderBookData):
        print("Order Event Received")
        print(f"Symbol        : {data.symbol}")
        print(f"Client        : {data.client}")
        print(f"Order Side    : {data.side}")
        print(f"Quantity      : {data.qty_remaining}")
        print(f"Status        : {data.status}")
        print(f"Exchange Order No: {data.exchange_order_no}")
        print(f"Entry Time    : {data.entry_at}")
        print("-" * 40)


```

---

## ⚠️ Notes

- Always ensure you have valid `app_key`, `secret_key`, `source`, and `user_id` for authentication.
- WebSocket callbacks like `onOrderEventReceived`, `onTradeEventReceived` automatically handle incoming events.
- All user credentials and authentication info are saved in a `.env` file on first run. No need to pass them again manually.

---

## 📁 Suggested Folder Structure

```
/your-project-root
|-- /venv
|-- .env
|-- main.py
|-- README.md
```

---

## 🙌 Support

Feel free to open an issue or reach out if you face any problems.

Happy Trading! 🚀
