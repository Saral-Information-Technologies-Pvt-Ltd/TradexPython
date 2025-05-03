import time

from tradex_client.tradex_api_client import TradeXClient

from tradex_client.exceptions import TradeXAPIError,TradeXDataFetchError,TradeXInvalidResponseError

from tradex_client.models import *
import json
import os
import sys
from datetime import datetime, timedelta

class TradeXTester:
    def __init__(self):
        try:
            self.client = TradeXClient(
                app_key="test",
                secret_key="test",
                base_url="https://tradex.saral-info.com:30001/TradeXApi/v1",
                client_id="test01",
                user_id="test01"
            )
            
            print(json.dumps(self.client.login(True).get_dict(), indent=2))
            self.client_id = self.client.client_id
            self.reference_values = {
                "exchanges": ["NseCm", "NseFO", "Bse", "BseFO", "NseCD", "MCX", "Ncdex", "BseCD", "NseCO", "OFS", "BseCO"],
                "sides": ["Buy", "Sell"],
                "products": ["Normal", "Intraday", "CNC", "MTF"],
                "books": ["RL", "SL", "PO", "CA2"],
                "validity": ["Day", "IOC", "GTD", "GTC", "EOD", "EOSES"],
                "common_codes": {
                    "NseCm": ["17818", "2885"],
                    "Bse": ["500325", "532540"],
                    "NseFO": ["73537"]
                }
            }
            print("TradeX Client initialized successfully.")
            connection_success = self.client.start_websocket()
            print(f"WebSocket Connection Success: {connection_success}")
            
            self.client.register_callback("order", self.handle_order_event)
            self.client.register_callback("trade", self.handle_trade_event)
            
            if not connection_success:
                print("Failed to connect WebSocket. Test aborted.")
                return
            
            time.sleep(2)
        except Exception as e:
            print(f"Failed to initialize TradeX Client: {e}")
            sys.exit(1)
    
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
    
    def prompt_for_value(self, prompt, options=None, default=None, data_type=str):
        if options:
            option_str = "\n".join([f"{i+1}: {opt}" for i, opt in enumerate(options)])
            print(f"{prompt}\n{option_str}")
            try:
                choice = input(f"Enter your choice (1-{len(options)}) [default: {default}]: ")
                if not choice.strip() and default is not None:
                    return default
                return options[int(choice)-1]
            except (ValueError, IndexError):
                print("Invalid selection. Using default value.")
                return default
        else:
            value = input(f"{prompt} [default: {default}]: ")
            if not value.strip() and default is not None:
                return default
            try:
                return data_type(value)
            except ValueError:
                print(f"Invalid input. Using default value: {default}")
                return default
    
    def print_response(self, response):
        """Print API response in a clean format"""
        if hasattr(response, 'get_dict'):
            print(json.dumps(response.get_dict(), indent=2))
        elif hasattr(response, 'data'):
            if isinstance(response.data, list):
                for item in response.data:
                    if hasattr(item, 'get_dict'): 
                        print(json.dumps(item.get_dict(), indent=2))
                    else:
                        print(item)
            elif hasattr(response.data, 'get_dict'):
                print(json.dumps(response.data.get_dict(), indent=2))
            else:
                print(response.data)
        else:
            print(response)
    
    def test_get_user_profile(self):
        """Test get_user_profile method"""
        try:
            response = self.client.get_user_profile()
            print("\nUser Profile:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_user_profile: {e}")
            return False
    
    def test_get_order_book(self):
        """Test get_order_book method"""
        try:
            filter_type = self.prompt_for_value(
                "Choose order book filter", 
                options=["All", "Pending"], 
                default="All"
            )
            response = self.client.get_order_book(filter_type)
            print(f"\nOrder Book ({filter_type}):")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_order_book: {e}")
            return False
    
    def test_get_trades_book(self):
        """Test get_trades_book method"""
        try:
            response = self.client.get_trades_book()
            print("\nTrades Book:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_trades_book: {e}")
            return False
    
    def test_place_new_order(self):
        """Test place_new_order method"""
        try:
            if not self.client_id:
                print("Client ID not set. Please set client ID first.")
                self.set_client_id()
            
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="NseFO"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="73537")
            
            side = self.prompt_for_value(
                "Choose side", 
                options=self.reference_values["sides"], 
                default="Buy"
            )
            
            quantity = self.prompt_for_value("Enter quantity", default=500, data_type=int)
            price = self.prompt_for_value("Enter price", default=1210.00, data_type=float)
            
            book = self.prompt_for_value(
                "Choose book", 
                options=self.reference_values["books"], 
                default="RL"
            )
            
            trigger_price = self.prompt_for_value("Enter trigger price", default=0, data_type=int)
            disclosed_qty = self.prompt_for_value("Enter disclosed quantity", default=0, data_type=int)
            
            product = self.prompt_for_value(
                "Choose product", 
                options=self.reference_values["products"], 
                default="Normal"
            )
            
            validity = self.prompt_for_value(
                "Choose validity", 
                options=self.reference_values["validity"], 
                default="Day"
            )
            
            gtd = self.prompt_for_value("Enter gtd", default="")
            order_flag = self.prompt_for_value("Enter order flag", default=4, data_type=int)
            sender_order_no = self.prompt_for_value("Enter sender order no", default=1512, data_type=int)
            algol_id = self.prompt_for_value("Enter algol id", default=1001, data_type=int)
            
            new_order_request = NewOrderRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "side": side,
                  "quantity": quantity,
                  "price": price,
                  "book": book,
                  "trigger_price": trigger_price,
                  "disclosed_qty": disclosed_qty,
                  "product": product,
                  "validity": validity,
                  "gtd": gtd,
                  "order_flag": order_flag,
                  "sender_order_no": sender_order_no,
                  "algol_id": algol_id,
                  "client": self.client_id
                }
            )
            
            response = self.client.place_new_order(new_order_request)
            print("\nNew Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in place_new_order: {e}")
            return False
    
    def test_modify_order(self):
        """Test modify_order method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="Bse"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="500325")
            
            exchange_order_no = self.prompt_for_value("Enter exchange order no", default="1742533817333000151")
            
            side = self.prompt_for_value(
                "Choose side", 
                options=self.reference_values["sides"], 
                default="Buy"
            )
            
            quantity = self.prompt_for_value("Enter quantity", default=15, data_type=int)
            price = self.prompt_for_value("Enter price", default=2795.75, data_type=float)
            
            book = self.prompt_for_value(
                "Choose book", 
                options=self.reference_values["books"], 
                default="RL"
            )
            
            trigger_price = self.prompt_for_value("Enter trigger price", default=0, data_type=int)
            disclosed_qty = self.prompt_for_value("Enter disclosed quantity", default=0, data_type=int)
            
            product = self.prompt_for_value(
                "Choose product", 
                options=self.reference_values["products"], 
                default="CNC"
            )
            
            validity = self.prompt_for_value(
                "Choose validity", 
                options=self.reference_values["validity"], 
                default="Day"
            )
            
            gtd = self.prompt_for_value("Enter gtd", default="")
            order_flag = self.prompt_for_value("Enter order flag", default=0, data_type=int)
            sender_order_no = self.prompt_for_value("Enter sender order no", default=1502, data_type=int)
            qty_remaining = self.prompt_for_value("Enter quantity remaining", default=10, data_type=int)
            qty_traded = self.prompt_for_value("Enter quantity traded", default=0, data_type=int)
            
            modify_order_request = ModifyOrderRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "exchange_order_no": exchange_order_no,
                  "side": side,
                  "quantity": quantity,
                  "price": price,
                  "book": book,
                  "trigger_price": trigger_price,
                  "disclosed_qty": disclosed_qty,
                  "product": product,
                  "validity": validity,
                  "gtd": gtd,
                  "order_flag": order_flag,
                  "sender_order_no": sender_order_no,
                  "qty_remaining": qty_remaining,
                  "qty_traded": qty_traded
                }
            )
            
            response = self.client.modify_order(modify_order_request)
            print("\nModify Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in modify_order: {e}")
            return False
    
    def test_cancel_order(self):
        """Test cancel_order method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="Bse"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="500325")
            
            sender_order_no = self.prompt_for_value("Enter sender order no", default=1503, data_type=int)
            user_order_no = self.prompt_for_value("Enter user order no", default="21")
            exchange_order_no = self.prompt_for_value("Enter exchange order no", default="1742533817333000151")
            
            cancel_order_request = CancelOrderRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "sender_order_no": sender_order_no,
                  "user_order_no": user_order_no,
                  "exchange_order_no": exchange_order_no
                }
            )
            
            response = self.client.cancel_order(cancel_order_request)
            print("\nCancel Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in cancel_order: {e}")
            return False
    
    def test_cancel_all_orders(self):
        """Test cancel_all_orders method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="Bse"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="500325")
            
            cancel_all_orders_request = CancelAllOrderRequest(
                **{
                  "exchange": exchange,
                  "code": code
                }
            )
            
            response = self.client.cancel_all_orders(cancel_all_orders_request)
            print("\nCancel All Orders Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in cancel_all_orders: {e}")
            return False
    
    def test_place_new_gtt_order(self):
        """Test place_new_gtt_order method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="NseCm"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="17818")
            
            side = self.prompt_for_value(
                "Choose side", 
                options=self.reference_values["sides"], 
                default="Buy"
            )
            
            product = self.prompt_for_value(
                "Choose product", 
                options=self.reference_values["products"], 
                default="CNC"
            )
            
            qty = self.prompt_for_value("Enter quantity", default=5, data_type=int)
            main_trigger_price = self.prompt_for_value("Enter main trigger price", default=4450, data_type=int)
            main_order_price = self.prompt_for_value("Enter main order price", default="4455")
            main_state = self.prompt_for_value("Enter main state", default="Scheduled")
            price_condition = self.prompt_for_value("Enter price condition", default="PriceAbove")
            stop_state = self.prompt_for_value("Enter stop state", default="None")
            stop_trigger_price = self.prompt_for_value("Enter stop trigger price", default=0, data_type=int)
            stop_order_price = self.prompt_for_value("Enter stop order price", default="")
            trail_gap = self.prompt_for_value("Enter trail gap", default=5.50, data_type=float)
            target_state = self.prompt_for_value("Enter target state", default="Scheduled")
            target_trigger_price = self.prompt_for_value("Enter target trigger price", default=4650, data_type=int)
            target_order_price = self.prompt_for_value("Enter target order price", default="Active3")
            sender_order_no = self.prompt_for_value("Enter sender order no", default=1515, data_type=int)
            
            new_gtt_order_request = NewGttOrderRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "side": side,
                  "product": product,
                  "qty": qty,
                  "main_trigger_price": main_trigger_price,
                  "main_order_price": main_order_price,
                  "main_state": main_state,
                  "price_condition": price_condition,
                  "stop_state": stop_state,
                  "stop_trigger_price": stop_trigger_price,
                  "stop_order_price": stop_order_price,
                  "trail_gap": trail_gap,
                  "target_state": target_state,
                  "target_trigger_price": target_trigger_price,
                  "target_order_price": target_order_price,
                  "sender_order_no": sender_order_no
                }
            )
            
            response = self.client.place_new_gtt_order(new_gtt_order_request)
            print("\nNew GTT Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in place_new_gtt_order: {e}")
            return False
    
    def test_modify_gtt_order(self):
        """Test modify_gtt_order method"""
        try:
            gtt_order_no = self.prompt_for_value("Enter GTT order no", default=5, data_type=int)
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="NseCm"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="2885")
            
            side = self.prompt_for_value(
                "Choose side", 
                options=self.reference_values["sides"], 
                default="Buy"
            )
            
            product = self.prompt_for_value(
                "Choose product", 
                options=self.reference_values["products"], 
                default="CNC"
            )
            
            qty = self.prompt_for_value("Enter quantity", default=1, data_type=int)
            price_condition = self.prompt_for_value("Enter price condition", default="string")
            main_trigger_price = self.prompt_for_value("Enter main trigger price", default=0, data_type=int)
            main_order_price = self.prompt_for_value("Enter main order price", default="string")
            main_state = self.prompt_for_value("Enter main state", default="string")
            stop_state = self.prompt_for_value("Enter stop state", default="string")
            stop_trigger_price = self.prompt_for_value("Enter stop trigger price", default=0, data_type=int)
            stop_order_price = self.prompt_for_value("Enter stop order price", default="string")
            trail_gap = self.prompt_for_value("Enter trail gap", default=0, data_type=float)
            target_state = self.prompt_for_value("Enter target state", default="string")
            target_trigger_price = self.prompt_for_value("Enter target trigger price", default=0, data_type=int)
            target_order_price = self.prompt_for_value("Enter target order price", default="string")
            sender_order_no = self.prompt_for_value("Enter sender order no", default=0, data_type=int)
            
            modify_gtt_order_request = ModifyGTTOrderRequest(
                **{
                  "gtt_order_no": gtt_order_no,
                  "exchange": exchange,
                  "code": code,
                  "side": side,
                  "product": product,
                  "qty": qty,
                  "price_condition": price_condition,
                  "main_trigger_price": main_trigger_price,
                  "main_order_price": main_order_price,
                  "main_state": main_state,
                  "stop_state": stop_state,
                  "stop_trigger_price": stop_trigger_price,
                  "stop_order_price": stop_order_price,
                  "trail_gap": trail_gap,
                  "target_state": target_state,
                  "target_trigger_price": target_trigger_price,
                  "target_order_price": target_order_price,
                  "sender_order_no": sender_order_no
                }
            )
            
            response = self.client.modify_gtt_order(modify_gtt_order_request)
            print("\nModify GTT Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in modify_gtt_order: {e}")
            return False
    
    def test_cancel_gtt_order(self):
        """Test cancel_gtt_order method"""
        try:
            gtt_order_no = self.prompt_for_value("Enter GTT order no", default=987654321, data_type=int)
            
            response = self.client.cancel_gtt_order(gtt_order_no)
            print("\nCancel GTT Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in cancel_gtt_order: {e}")
            return False
    
    def test_execute_basket_order(self):
        """Test execute_basket_order method"""
        try:
            # For simplicity, using empty request - modify as needed
            basket_order_request = ExecuteBasketOrderRequest()
            
            response = self.client.execute_basket_order(basket_order_request)
            print("\nBasket Order Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in execute_basket_order: {e}")
            return False
    
    def test_get_order_status(self):
        """Test get_order_status method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="Bse"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="500325")
            
            exchange_order_no = self.prompt_for_value("Enter exchange order no", default="")
            sender_order_no = self.prompt_for_value("Enter sender order no", default=1502, data_type=int)
            
            order_status_request = OrderStatusRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "exchange_order_no": exchange_order_no,
                  "sender_order_no": sender_order_no
                }
            )
            
            response = self.client.get_order_status(order_status_request)
            print("\nOrder Status Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_order_status: {e}")
            return False
    
    def test_get_order_history(self):
        """Test get_order_history method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="NseCm"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="2885")
            
            exchange_order_no = self.prompt_for_value("Enter exchange order no", default="")
            sender_order_no = self.prompt_for_value("Enter sender order no", default=1505, data_type=int)
            
            order_history_request = OrderHistoryRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "exchange_order_no": exchange_order_no,
                  "sender_order_no": sender_order_no
                }
            )
            
            response = self.client.get_order_history(order_history_request)
            print("\nOrder History Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_order_history: {e}")
            return False
    
    def test_get_holdings(self):
        """Test get_holdings method"""
        try:
            response = self.client.get_holdings()
            print("\nHoldings:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_holdings: {e}")
            return False
    
    def test_get_positions(self):
        """Test get_positions method"""
        try:
            response = self.client.get_positions()
            print("\nPositions:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_positions: {e}")
            return False
    
    def test_convert_position(self):
        """Test convert_position method"""
        try:
            exchange = self.prompt_for_value(
                "Choose exchange", 
                options=self.reference_values["exchanges"], 
                default="Bse"
            )
            
            codes = self.reference_values["common_codes"].get(exchange, [])
            if codes:
                code = self.prompt_for_value("Choose code", options=codes, default=codes[0])
            else:
                code = self.prompt_for_value("Enter code", default="500325")
            
            old_product = self.prompt_for_value(
                "Choose old product", 
                options=self.reference_values["products"], 
                default="CNC"
            )
            
            new_product = self.prompt_for_value(
                "Choose new product", 
                options=self.reference_values["products"], 
                default="Normal"
            )
            
            side = self.prompt_for_value(
                "Choose side", 
                options=self.reference_values["sides"], 
                default="Buy"
            )
            
            qty = self.prompt_for_value("Enter quantity", default=5, data_type=int)
            
            convert_position_request = ConvertPositionRequest(
                **{
                  "exchange": exchange,
                  "code": code,
                  "old_product": old_product,
                  "new_product": new_product,
                  "side": side,
                  "qty": qty
                }
            )
            
            response = self.client.convert_position(convert_position_request)
            print("\nConvert Position Response:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in convert_position: {e}")
            return False
    
    def test_get_funds_report(self):
        """Test get_funds_report method"""
        try:
            response = self.client.get_funds_report()
            print("\nFunds Report:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_funds_report: {e}")
            return False
    
    def test_get_exchange_status(self):
        """Test get_exchange_status method"""
        try:
            response = self.client.get_exchange_status()
            print("\nExchange Status:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in get_exchange_status: {e}")
            return False
    
    def test_logout(self):
        """Test logout method"""
        try:
            response = self.client.logout()
            print("\nLogout Successful:")
            self.print_response(response)
            return True
        except Exception as e:
            print(f"Error in logout: {e}")
            return False
    
    def run(self):
        """Main method to run test cases"""
        tests = {
            1: {"name": "Get User Profile", "method": self.test_get_user_profile},
            2: {"name": "Get Order Book", "method": self.test_get_order_book},
            3: {"name": "Get Trades Book", "method": self.test_get_trades_book},
            4: {"name": "Place New Order", "method": self.test_place_new_order},
            5: {"name": "Modify Order", "method": self.test_modify_order},
            6: {"name": "Cancel Order", "method": self.test_cancel_order},
            7: {"name": "Cancel All Orders", "method": self.test_cancel_all_orders},
            8: {"name": "Get Order Status", "method": self.test_get_order_status},
            9: {"name": "Get Order History", "method": self.test_get_order_history},
            10: {"name": "Get Holdings", "method": self.test_get_holdings},
            11: {"name": "Get Positions", "method": self.test_get_positions},
            12: {"name": "Convert Position", "method": self.test_convert_position},
            13: {"name": "Get Funds Report", "method": self.test_get_funds_report},
            14: {"name": "Get Exchange Status", "method": self.test_get_exchange_status},
            0: {"name": "Exit", "method": self.test_logout}
        }
        
        while True:
            print("\n\n===== TradeX Client Test Menu =====")
            for key, test in tests.items():
                print(f"{key}: {test['name']}")
            print("=================================")
            
            choice = input("Enter your choice (0-18): ")
            try:
                choice = int(choice)
                if choice == 0:
                    print("Exiting...")
                    self.test_logout()
                    break
                elif choice in tests:
                    print(f"\nRunning test: {tests[choice]['name']}")
                    tests[choice]['method']()
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except Exception as e:
                print(f"Error: {e}")
            
            input("\nPress Enter to continue...")

def main():
    try:
        tester = TradeXTester()
        tester.run()
    except TradeXDataFetchError as e:
        print(f"Data Fetch Error: {e}")
    except TradeXInvalidResponseError as e: 
        print(f"Invalid Response Error: {e}")
    except TradeXAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()