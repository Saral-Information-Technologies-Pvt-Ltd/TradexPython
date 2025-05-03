from datetime import datetime, timedelta
import requests
from dataclasses import asdict
from dotenv import load_dotenv, set_key, get_key
import os
import json
from urllib.parse import urlparse
from tradex_client.models.cancel_all_orders import CancelAllOrderRequest,CancelAllOrderResponse

from tradex_client.models.cancel_gtt_order import CancelGTTOrderData, CancelGTTOrderResponse
from tradex_client.models.cancel_order import CancelOrderRequest, CancelOrderData, CancelOrderResponse
from tradex_client.models.convert_position import ConvertPositionRequest, ConvertPositionData, ConvertPositionResponse
from tradex_client.models.exchange_status import ExchangeStatusData, ExchangeStatusResponse
from tradex_client.models.execute_basket_orders import ExecuteBasketOrderRequest, ExecuteBasketData, ExecuteBasketResponse
from tradex_client.models.funds_report import FundsReportData, FundsReportResponse
from tradex_client.models.gtt_order_book import GTTOrderBookData, GTTOrdersBookResponse
from tradex_client.models.holdings import HoldingsData, HoldingsResponse
from tradex_client.models.login import LoginRequest, LoginData, LoginResponse
from tradex_client.models.logout import LogoutData
from tradex_client.models.modify_gtt_order import ModifyGTTOrderRequest, ModifyGTTOrderData, ModifyGTTOrderResponse
from tradex_client.models.modify_order import ModifyOrderRequest, ModifyOrderData, ModifyOrderResponse
from tradex_client.models.new_gtt_order import NewGttOrderRequest, NewGttOrderData, NewGttOrderResponse
from tradex_client.models.new_order import NewOrderRequest, NewOrderData, NewOrderResponse
from tradex_client.models.order_history import OrderHistoryRequest, OrderHistoryData, OrderHistoryResponse
from tradex_client.models.order_status import OrderStatusRequest, OrderStatusData, OrderStatusResponse
from tradex_client.models.orders_book import OrderBookResponse, OrderBookData
from tradex_client.models.positions import NetPositionData, NetPositionResponse
from tradex_client.models.trades_book import TradesBookData, TradesBookResponse
from tradex_client.models.user_profile import UserProfileData, UserProfileResponse

from tradex_client.exceptions import TradeXAPIError, TradeXAuthenticationError, TradeXDataFetchError, TradeXInvalidResponseError
from tradex_client.tradex_websocket_client import TradeXWebSocketClient

class TradeXClient:
    """
    Client for interacting with the TradeX trading API.
    
    This class provides methods for authentication, order management, portfolio information, 
    and market data access through the TradeX API. It handles credential management, token-based
    authentication, and request/response formatting for all API endpoints.
    
    The client supports loading credentials from environment variables, .env files, or direct
    parameter passing, and can optionally save credentials to a .env file for later use.
    
    Attributes:
        debug (bool): Flag to enable verbose debug output
        app_key (str): API key for authentication
        secret_key (str): Secret key for authentication
        base_url (str): Base URL for the TradeX API
        websocket_host (str): Websocket host for the TradeX API
        websocket_port (str): Websocket port for the TradeX API
        timeout (int): Request timeout in seconds
        request_session (requests.Session): Session for making HTTP requests
        token (str): Authentication token received after login
        client_id (str): Client ID received after login
        user_id (str): User ID received after login
        headers (dict): HTTP headers used for API requests
        env_file (str): Path to the environment file
        
    Raises:
        ValueError: If required credentials are missing or invalid
    """
    def __init__(self, app_key: str, secret_key: str, base_url: str=None, websocket_url: str="wss://tradex.saral-info.com:30001", client_id: str=None, user_id: str=None, debug=False, timeout=7, env_file='.env'):
        """
        Initialize the TradeXClient with authentication credentials and settings.
        
        The client will attempt to load credentials from the provided parameters first,
        then fall back to environment variables or the specified .env file. When new credentials
        are provided directly, they can be automatically saved to the .env file for future use.
        
        Args:
            app_key (str, optional): API key for authentication. If None, will be loaded from environment.
            secret_key (str, optional): Secret key for authentication. If None, will be loaded from environment.
            base_url (str, optional): Base URL for the TradeX API. If None, will be loaded from environment.
            websocket_url (str, optional): Websocket URL for the TradeX API. If None, will be loaded from environment.
            client_id (str, optional): Client ID for authentication. If None, will be loaded from environment.
            user_id (str, optional): User ID for API calls. If None, will be loaded from environment.
            debug (bool, optional): Enable debug mode for verbose output. Defaults to False.
            timeout (int, optional): Request timeout in seconds. Defaults to 7.
            env_file (str, optional): Path to .env file. Defaults to '.env'.
            
        Raises:
            ValueError: If API key, secret key, base URL, websocket URL, client ID or user ID are missing,
                or if client ID or user ID exceed length limits.
        """
        self.env_file = env_file
        load_dotenv(dotenv_path=self.env_file)
        
        self.debug = debug
        self.base_url = base_url
        self.timeout = timeout
        self.request_session = requests.Session()
        
        save_to_env = False
        
        self.app_key = app_key
        self.secret_key = secret_key
        
        # Load and validate base URL
        env_base_url = os.environ.get('BASE_URL')
        if base_url and (not env_base_url or env_base_url != base_url):
            save_to_env = True
        self.base_url = base_url or env_base_url
        
        if websocket_url:
            parsed_url = urlparse(websocket_url)
            self.websocket_host = parsed_url.hostname
            self.websocket_port = int(parsed_url.port)
        else:
            self.websocket_host = ''
            self.websocket_port = 0
        
        # Load and validate websocket host
        env_websocket_host = os.environ.get('WEBSOCKET_HOST')
        if self.websocket_host and (not env_websocket_host or env_websocket_host != self.websocket_host):
            save_to_env = True
        self.websocket_host = self.websocket_host or env_websocket_host
        
        # Load and validate websocket port
        env_websocket_port = os.environ.get('WEBSOCKET_PORT')
        if self.websocket_port and (not env_websocket_port or env_websocket_port != self.websocket_port):
            save_to_env = True
        self.websocket_port = self.websocket_port or env_websocket_port
        
        if self.debug:
            print(self.websocket_host, self.websocket_port)
        
        # Load and validate client ID
        env_client_id = os.environ.get('CLIENT_ID')
        if client_id and (not env_client_id or env_client_id.upper() != client_id.upper()):
            save_to_env = True
        self.client_id = client_id or env_client_id
        self.client_id = self.client_id.upper().strip() if self.client_id else None
        
        # Load and validate user ID
        env_user_id = os.environ.get('USER_ID')
        if user_id and (not env_user_id or env_user_id.upper() != user_id.upper()):
            save_to_env = True
        self.user_id = user_id or env_user_id
        self.user_id = self.user_id.upper().strip() if self.user_id else None
        
        self.token = None
        
        self.headers = {
            "Content-Type": "application/json",
        }
        
        self.websocket_magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        
        # Validate required credentials
        if not self.app_key or not self.secret_key or not self.client_id:
            raise ValueError("API key, secret key, base url, websocket url, client ID and user ID must be provided")
        
        # Validate client ID length
        if len(self.client_id) > 10:
            self.client_id = None
            raise ValueError('Client ID cannot exceed length of 10 characters.')
        
        # Validate user ID length
        if len(self.user_id) > 10:
            self.user_id = None
            raise ValueError('User ID cannot exceed length of 10 characters.')
        
        # Set credentials and perform login
        self.set_credentials(self.client_id, self.user_id, self.base_url, self.websocket_host, self.websocket_port, save_to_env)

        self.websocket_client = None
        self.websocket_running = False
    
    def set_credentials(self, client_id, user_id, base_url, websocket_host, websocket_port, save_to_env=False):
        """
        Set API credentials for the client and initialize the session.
        
        This method updates the client's credentials, optionally saves them to the environment file,
        and performs automatic login to obtain an authentication token.
        
        Args:
            client_id (str): Client ID for identification
            user_id (str): User ID for identification
            base_url (str): Base URL for the TradeX API
            websocket_host (str): Websocket host for the TradeX API
            websocket_port (str): Websocket port for the TradeX API
            save_to_env (bool, optional): Whether to save credentials to .env file. Defaults to False.
            
        Raises:
            TradeXAuthenticationError: If login fails with the provided credentials
        """
        self.client_id = client_id.upper()
        self.user_id = user_id.upper()
        self.base_url = base_url
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        
        if save_to_env:
            self.__save_credentials_to_env()
        
        # self.login()
        
    def __save_credentials_to_env(self):
        """
        Save the current credentials to the .env file.
        
        This method updates or creates environment variables in the specified .env file
        with the current client credentials. This allows the credentials to be reused
        in future sessions without explicit specification.
        """
        set_key(self.env_file, 'CLIENT_ID', self.client_id)
        set_key(self.env_file, 'USER_ID', self.user_id)
        set_key(self.env_file, 'BASE_URL', self.base_url)
        set_key(self.env_file, 'WEBSOCKET_HOST', self.websocket_host)
        set_key(self.env_file, 'WEBSOCKET_PORT', str(self.websocket_port))
        
        if self.debug:
            print("Credentials saved to", self.env_file)
        
    # -------------------------------------------------------------------------
    # USER ENDPOINTS
    # -------------------------------------------------------------------------
    
    def __check_existing_token(self):
        """
        Check if a valid token exists in the .env file.
        
        Returns:
            bool: True if a valid token exists, False otherwise
        """
        token = get_key(self.env_file, 'TOKEN')
        token_expiry = get_key(self.env_file, 'TOKEN_EXPIRY')
        
        if not token or not token_expiry:
            return False
        
        try:
            expiry_time = datetime.fromisoformat(token_expiry)
            if datetime.now() + timedelta(minutes=5) < expiry_time:
                self.token = token
                self.headers["Authorization"] = f"Bearer {self.token}"
                return True
            else:
                if self.debug:
                    print("Token expired, will get a new one")
                return False
        except (ValueError, TypeError):
            if self.debug:
                print("Error parsing token expiry time, will get a new one")
            return False

    def __save_token_to_env(self, token, expiry_hours=24):
        """
        Save the authentication token and its expiry time to the .env file.
        
        Args:
            token (str): The authentication token
            expiry_hours (int): Token validity period in hours
        """
        expiry_time = datetime.now() + timedelta(hours=expiry_hours)
        set_key(self.env_file, 'TOKEN', token)
        set_key(self.env_file, 'TOKEN_EXPIRY', expiry_time.isoformat())
        
        if self.debug:
            print(f"Token saved to {self.env_file}, expires at {expiry_time}")

    def login(self, get_new_token: bool=False):
        """
        Authenticate with the TradeX API using API key and secret key.
        
        This method first checks for an existing valid token in the environment.
        If no valid token is found, it establishes a new session with the API by
        validating the credentials and stores the authentication token for
        subsequent API calls.
        
        Raises:
            TradeXAuthenticationError: If login fails due to invalid credentials or if
                the response is missing required fields
        """
        if self.__check_existing_token() and not get_new_token:
            if self.debug:
                print("Using existing token from environment file")
            return LoginResponse(status="OK", message="Using existing token", data=None)
        
        login_payload = {
            "user_id": f"{self.user_id}",
            "app_key": f"{self.app_key}",
            "secret_key": f"{self.secret_key}",
            "source": "Test"
        }
        
        response = self._post('Login', payload=login_payload) 

        if not response or "data" not in response:
            raise TradeXAuthenticationError("Login failed. No valid response received.")
        
        data = response["data"]
        self.login_data = LoginData(**data)
        
        if self.debug:
            print(json.dumps(self.login_data.get_dict(), indent=2))
        
        if "token" not in data or "user_id" not in data:
            raise TradeXAuthenticationError("Login response is missing required fields.")
        
        self.token = data["token"]
        self.user_id = data["user_id"]
        self.headers["Authorization"] = f"Bearer {self.token}"
        
        self.__save_token_to_env(self.token)
        
        return LoginResponse(status=response.get('status'), message=response.get('message'), data=self.login_data)
    
    def logout(self):
        """
        Log out from the TradeX API.
        
        This method terminates the current API session, invalidating the authentication token.
        After logout, subsequent API calls will fail until a new login is performed.
        It also removes the token and token expiry entries from the environment file.
        
        Returns:
            dict: The API response containing logout status and message
            
        Raises:
            TradeXAPIError: If the logout request fails
        """
        params = {
            "ClientID": self.user_id
        }
        response = self._post('Logout', params=params)
        
        # Remove token information from .env file
        set_key(self.env_file, 'TOKEN', '')
        set_key(self.env_file, 'TOKEN_EXPIRY', '')
        
        # Reset token attribute
        self.token = None
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
        
        # Close websocket connection if active
        if self.websocket_client:
            self.websocket_client.stop()
        
        if self.debug:
            print("Logged out and removed token from environment file")
        
        return response
        
    def get_user_profile(self):
        """
        Fetch the user profile information.
        
        This method retrieves detailed information about the authenticated user's profile,
        including personal details, account settings, and preferences.
        
        Returns:
            UserProfileResponse: Object containing user profile data with fields such as
                name, email, phone, address, and account settings
                
        Raises:
            TradeXAPIError: If the API request fails
            TradeXDataFetchError: If the user profile data cannot be retrieved
        """
        params = {
            "ClientID": self.client_id  
        }
        response = self._post('UserProfile', params=params)
        return UserProfileResponse(status=response.get('status'), message=response.get('message'), data=UserProfileData(**response.get('data')))
    
    
    # -------------------------------------------------------------------------
    # ORDERS ENDPOINTS
    # -------------------------------------------------------------------------
    
    def place_new_order(self, new_order_details: NewOrderRequest):
        """
        Place a new trading order.
        
        This method sends a new order request to the trading platform with the specified
        parameters such as symbol, quantity, price, order type, etc.
        
        Args:
            new_order_details (NewOrderRequest): Order details.
            
        Returns:
            NewOrderResponse: Object containing order status and confirmation details,
                including the assigned order ID and exchange order number
                
        Raises:
            TradeXAPIError: If the order placement fails due to API errors
            TradeXInvalidResponseError: If the order parameters are invalid
        """

        new_order_details.client = self.client_id
        order_payload = new_order_details.get_dict()
        response = self._post('NewOrder', payload=order_payload)
        return NewOrderResponse(status=response.get('status'), message=response.get('message'), data=NewOrderData(**response.get('data')))
    
    def modify_order(self, modify_order_details: ModifyOrderRequest):
        """
        Modify an existing order.
        
        This method updates the parameters of an existing order that has not yet been
        fully executed. Typical modifications include price, quantity, or order type changes.
        
        Args:
            modify_order_details (ModifyOrderRequest): Modified order details.
            
        Returns:
            ModifyOrderResponse: Object containing status of the modification and
                updated order details
                
        Raises:
            TradeXAPIError: If the order modification fails
            TradeXInvalidResponseError: If the modification parameters are invalid
            TradeXDataFetchError: If the original order cannot be found
        """
        order_payload = modify_order_details.get_dict()
        response = self._post('ModifyOrder', payload=order_payload)
        return ModifyOrderResponse(status=response.get('status'), message=response.get('message'), data=ModifyOrderData(**response.get('data')))    
    
    def cancel_order(self, cancel_order_details: CancelOrderRequest):
        """
        Cancel an existing order.
        
        This method cancels a specific order that has not yet been fully executed.
        Partial cancellations are not supported - the entire remaining unexecuted
        quantity will be cancelled.
        
        Args:
            cancel_order_details (CancelOrderRequest): Details of the order to cancel.
            
        Returns:
            CancelOrderResponse: Object containing cancellation status and details
                of the cancelled order
                
        Raises:
            TradeXAPIError: If the cancellation request fails
            TradeXDataFetchError: If the specified order cannot be found
        """
        order_payload = cancel_order_details.get_dict()
        response = self._post('CancelOrder', payload=order_payload)
        return CancelOrderResponse(status=response.get('status'), message=response.get('message'), data=CancelOrderData(**response.get('data')))
    
    def cancel_all_orders(self, cancel_orders_detail: CancelAllOrderRequest):
        """
        Cancel all open orders for a specific exchange.
        
        This method cancels all pending orders for the specified exchange code. This is useful
        for quickly exiting all positions or clearing all pending orders in emergency situations
        or at the end of a trading day.
        
        Args:
            cancel_orders_detail (CancelAllOrderRequest): Details for cancelling all orders.
            
        Returns:
            CancelAllOrderResponse: Object containing cancellation status with a status code
                and message indicating success or failure
                
        Raises:
            TradeXAPIError: If the cancellation request fails
        """
        order_payload = cancel_orders_detail.get_dict()
        response = self._post('CancelAllOrders', payload=order_payload)
        
        return CancelAllOrderResponse(status=response.get('status'), message=response.get('message'))
    
    def place_new_gtt_order(self, new_order_details: NewGttOrderRequest):
        """
        Place a new Good-Till-Triggered (GTT) order.
        
        GTT orders are conditional orders that remain active until a specified price condition is met.
        They can include main orders, target orders, and stop-loss orders in a single request.
        
        Args:
            new_order_details (NewGttOrderRequest): GTT order details.
            
        Returns:
            NewGttOrderResponse: Object containing GTT order status and the assigned GTT order number
                
        Raises:
            TradeXAPIError: If the order placement fails
            TradeXInvalidResponseError: If the order parameters are invalid
        """
        order_payload = new_order_details.get_dict()
        response = self._post('NewGTTOrder', payload=order_payload)
        return NewGttOrderResponse(status=response.get('status'), message=response.get('message'), data=NewGttOrderData(**response.get('data')))
    
    def modify_gtt_order(self, modify_order_data: ModifyGTTOrderRequest):
        """
        Modify an existing GTT order.
        
        This method updates the parameters of an active Good-Till-Triggered order,
        including price conditions, order parameters, or validity period.
        
        Args:
            modify_order_data (ModifyGTTOrderRequest): Modified GTT order details.
            
        Returns:
            ModifyGTTOrderResponse: Object containing status of the modification
                and updated GTT order details
                
        Raises:
            TradeXAPIError: If the order modification fails
            TradeXInvalidResponseError: If the modification parameters are invalid
            TradeXDataFetchError: If the original GTT order cannot be found
        """
        order_payload = modify_order_data.get_dict()
        response = self._post('ModifyGTTOrder', payload=order_payload)
        return ModifyGTTOrderResponse(status=response.get('status'), message=response.get('message'), data=ModifyGTTOrderData(**response.get('data')))
    
    def cancel_gtt_order(self, gtt_order_no: int):
        """
        Cancel a GTT order.
        
        This method cancels a specific Good-Till-Triggered order identified by its GTT order number.
        Once cancelled, all conditions and pending actions associated with the GTT order are removed.
        
        Args:
            gtt_order_no (int): The GTT order number to cancel
            
        Returns:
            CancelGTTOrderResponse: Object containing cancellation status and details
                of the cancelled GTT order
                
        Raises:
            TradeXAPIError: If the cancellation request fails
            TradeXDataFetchError: If the specified GTT order cannot be found
        """
        params = {
            "ClientID": self.client_id,
            "GttOrderNo": gtt_order_no
        }
        response = self._post('CancelGTTOrder', params=params)
        return CancelGTTOrderResponse(data=CancelGTTOrderData(**response.get('data')), status=response.get('status'), message=response.get('message'))
    
    def execute_basket_order(self, order_details: ExecuteBasketOrderRequest):
        """
        Execute a basket order (multiple orders at once).
        
        This method allows submitting multiple orders simultaneously as a basket,
        which can be useful for portfolio rebalancing, strategy execution, or other
        scenarios requiring coordinated order placement.
        
        Args:
            order_details (ExecuteBasketOrderRequest): Basket order details including
                an array of individual order requests
            
        Returns:
            ExecuteBasketResponse: Object containing execution status for the entire
                basket and status details for each individual order
                
        Raises:
            TradeXAPIError: If the basket execution fails
            TradeXInvalidResponseError: If any order parameters are invalid
        """
        order_payload = self._get_dict(order_details)
        response = self._post('ExecuteBasket', payload=order_payload)
        return ExecuteBasketResponse(data=ExecuteBasketData(**response.get('data')), status=response.get('status'), message=response.get('message'))
    
    
    # -------------------------------------------------------------------------
    # BOOK ENDPOINTS
    # -------------------------------------------------------------------------
    
    def get_order_book(self, filter_type: str = 'All'):
        """
        Get the order book with filtering options.
        
        This method retrieves a list of orders matching the specified filter criteria.
        It provides information about order status, execution details, and other parameters.
        
        Args:
            filter_type (str, optional): Filter for order status. Defaults to 'All'.
                Valid options:
                - "All": All orders regardless of status
                - "Pending": Orders waiting to be executed
                - "Unconfirmed": Orders submitted but not yet confirmed
                - "Cancelled": Orders that have been cancelled
                - "Rejected": Orders rejected by the exchange
                - "Failed": Orders that failed to process
                - "Executed": Orders that have been fully executed
                
        Returns:
            OrderBookResponse: Object containing list of orders matching the filter criteria
            
        Raises:
            ValueError: If an invalid filter_type is provided
            TradeXAPIError: If the order book data cannot be retrieved
        """
        valid_filters = ["All", "Pending", "Unconfirmed", "Cancelled", "Rejected", "Failed", "Executed"]
        if filter_type not in valid_filters:
            list_filters = ', '.join(valid_filters)
            raise ValueError(f'Invalid filter type! Must be one of these: {list_filters}')
        
        params = {
            "ClientID": self.client_id,
            "Filter": filter_type
        }
        response = self._post('OrderBook', params=params)
        order_data_list = OrderBookData.parse_list(response)
        return OrderBookResponse(status=response.get('status'), message=response.get('message'), data=order_data_list)
    
    def get_order_status(self, order_details: OrderStatusResponse):
        """
        Get the status of a specific order.
        
        This method retrieves detailed information about a specific order,
        including its current status, filled quantity, average price, and other details.
        
        Args:
            order_details (OrderStatusResponse): Details of the order.s
            
        Returns:
            OrderStatusResponse: Object containing order status information with
                detailed execution and status data
                
        Raises:
            TradeXAPIError: If the status cannot be retrieved
            TradeXDataFetchError: If the specified order cannot be found
        """
        order_payload = self._get_dict(order_details)
        response = self._post('OrderStatus', payload=order_payload)
        order_data_list = OrderStatusData.parse_list(response)
        return OrderStatusResponse(status=response.get("status"), message=response.get("message"), data=order_data_list)
    
    def get_gtt_order_book(self):
        """
        Get the book of all GTT (Good-Till-Triggered) orders.
        
        This method retrieves a list of all active GTT orders for the client,
        including their trigger conditions, order parameters, and status.
        
        Returns:
            GTTOrdersBookResponse: Object containing list of GTT orders with
                detailed information about each order
                
        Raises:
            TradeXAPIError: If the GTT order data cannot be retrieved
        """
        params = {
            "ClientID": self.client_id
        }
        response = self._post('GttOrdersBook', params=params)
        order_data_list = GTTOrderBookData.parse_list(response)
        return GTTOrdersBookResponse(status=response.get("status"), message=response.get("message"), data=order_data_list)
    
    def get_trades_book(self):
        """
        Get the book of all executed trades.
        
        This method retrieves a list of all executed trades for the client,
        including details like symbol, quantity, price, trade time, etc.
        
        Returns:
            TradesBookResponse: Object containing list of trades with
                detailed information about each executed trade
                
        Raises:
            TradeXAPIError: If the trade data cannot be retrieved
        """
        params = {
            "ClientID": self.client_id
        }
        response = self._post('TradeBook', params=params)
        order_data_list = TradesBookData.parse_list(response)
        return TradesBookResponse(status=response.get("status"), message=response.get("message"), data=order_data_list)
    
    def get_order_history(self, client_details: OrderHistoryRequest):
        """
        Get the history of orders.
        
        This method retrieves the historical record of orders based on the specified
        criteria, including information about status changes, modifications, and execution.
        
        Args:
            client_details (OrderHistoryRequest): Details for the order history.
            
        Returns:
            OrderHistoryResponse: Object containing order history with chronological
                data about each order's lifecycle
                
        Raises:
            TradeXAPIError: If the history data cannot be retrieved
        """
        client_payload = self._get_dict(client_details)
        response = self._post('OrderHistory', payload=client_payload)
        order_data_list = OrderHistoryData.parse_list(response) 
        return OrderHistoryResponse(status=response.get("status"), message=response.get("message"), data=order_data_list)
    
    
    # -------------------------------------------------------------------------
    # PORTFOLIO ENDPOINTS
    # -------------------------------------------------------------------------
    
    def get_holdings(self):
        """
        Get the current holdings in the portfolio.
        
        This method retrieves a list of securities currently held in the portfolio,
        including details such as quantity, average price, current value, and profit/loss.
        
        Returns:
            HoldingsResponse: Object containing holdings information with
                detailed data for each holding
                
        Raises:
            TradeXAPIError: If the holdings data cannot be retrieved
        """
        params = {
            "ClientID": self.client_id
        }
        response = self._post('Holdings', params=params)
        holdings_list = HoldingsData.parse_list(response)
        return HoldingsResponse(status=response.get("status"), message=response.get("message"), data=holdings_list)
    
    def get_positions(self, filter_type: str='All'):
        """
        Get the current positions (open and closed).
        
        This method retrieves information about current market positions,
        including both intraday and delivery positions, with details about
        quantity, average price, current market value, and profit/loss.
        
        Args:
            filter_type (str, optional): Filter for position type. Defaults to 'All'.
                Valid options: 
                - 'All': All positions
                - 'Todays': Only today's positions
                - 'Opening': Only positions from previous days
                
        Returns:
            NetPositionResponse: Object containing positions information with
                detailed data for each position
                
        Raises:
            ValueError: If an invalid filter_type is provided
            TradeXAPIError: If the positions data cannot be retrieved
        """
        valid_filters = ['All', 'Todays', 'Opening']
        if filter_type not in valid_filters:
            list_filters = ', '.join(valid_filters)
            raise ValueError(f'Invalid filter type! must be one of these : {list_filters}')
        
        params = {
            "ClientID": self.client_id,  
            "Filter": filter_type
        }
        response = self._post('NetPositions', params=params)
        net_positions = NetPositionData.parse_list(response)
        return NetPositionResponse(status=response.get("status"), message=response.get("message"), data=net_positions)
    
    def convert_position(self, conversion_data: ConvertPositionRequest):
        """
        Convert position from one product type to another.
        
        This method changes the product type of an existing position, which can affect
        margin requirements, holding periods, and other trading parameters.
        
        Args:
            conversion_data (ConvertPositionRequest): Position conversion details
            
        Returns:
            ConvertPositionResponse: Object containing conversion status with
                details about the converted position
                
        Raises:
            TradeXAPIError: If the position conversion fails
            TradeXInvalidResponseError: If the conversion parameters are invalid
        """
        conversion_payload = self._get_dict(conversion_data)
        response = self._post('ModifyProduct', payload=conversion_payload)
        return ConvertPositionResponse(status=response.get('status'), message=response.get('message'), data=ConvertPositionData(**response.get('data')))
    
    
    # -------------------------------------------------------------------------
    # FUNDS ENDPOINTS
    # -------------------------------------------------------------------------
    
    def get_funds_report(self):
        """
        Get the funds report.
        
        This method retrieves detailed information about available funds, margins,
        collateral values, and other financial aspects of the trading account.
        
        Returns:
            FundsReportResponse: Object containing funds details
                
        Raises:
            TradeXAPIError: If the funds data cannot be retrieved
        """
        params = {
            "ClientID": self.client_id
        }
        response = self._post('FundsReport', params=params)
        funds_data = FundsReportData.parse_list(response)
        return FundsReportResponse(status=response.get("status"), message=response.get("message"), data=funds_data)
    
    
    # -------------------------------------------------------------------------
    # OTHER ENDPOINTS
    # -------------------------------------------------------------------------
    
    def get_exchange_status(self):
        """
        Get the status of various exchanges.
        
        This method retrieves the current connectivity status and trading status
        for the exchanges supported by the trading platform.
        
        Returns:
            ExchangeStatusResponse: Object containing exchange connectivity status
                with details for each exchange
                
        Raises:
            TradeXAPIError: If the exchange status data cannot be retrieved
        """
        params = {
            "ClientID": self.client_id
        }
        response = self._post('ExchangeStatus', params=params)
        exchange_data = ExchangeStatusData.parse_list(response)
        return ExchangeStatusResponse(status=response.get("status"), message=response.get("message"), data=exchange_data)

    
    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    
    def _get_dict(self, data_class):
        """
        Convert a dataclass instance to a dictionary.
        
        This is a utility method to convert dataclass objects to dictionaries
        for JSON serialization when making API requests.
        
        Args:
            data_class: Dataclass instance to convert
            
        Returns:
            dict: Dictionary representation of the dataclass
        """
        return asdict(data_class)
    
    def _post(self, endpoint: str, payload: dict=None, params: dict=None):
        """
        Make a POST request to the TradeX API.
        
        Args:
            endpoint (str): API endpoint to call
            payload (dict, optional): JSON payload for the request. Defaults to None.
            params (dict, optional): Query parameters for the request. Defaults to None.
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            TradeXAuthenticationError: For authentication failures (401)
            TradeXInvalidResponseError: For bad requests (400)
            TradeXDataFetchError: For no data found (404)
            TradeXAPIError: For other API errors
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = self.request_session.post(url, json=payload, params=params, headers=self.headers)
        
        if self.debug:
            print(response.text)
        
        try:
            response_json = response.json() if response.text else None

            if response_json is None:
                raise TradeXAPIError(f"Empty or invalid response from {endpoint}. Status Code: {response.status_code}")
            if response.status_code == 200:
                return response_json
            elif response.status_code == 202 and endpoint == 'CancelAllOrders':
                return response_json
            elif response.status_code == 401:
                raise TradeXAuthenticationError(
                    f"Unauthorized for endpoint: {endpoint}",
                    status_code=401, 
                    response_message=response_json.get("message", "No message"), 
                    response_data=response_json.get("data", {})
                )
            elif response.status_code == 500:
                raise TradeXAPIError(
                    f"Internal Server Error for endpoint: {endpoint}", 
                    status_code=500, 
                    response_message=response_json.get("message", "No message"), 
                    response_data=response_json.get("data", {})
                )
            elif response.status_code == 400:
                raise TradeXInvalidResponseError(
                    f"Bad Request for endpoint: {endpoint}", 
                    status_code=400, 
                    response_message=response_json.get("message", "No message"), 
                    response_data=response_json.get("data", {})
                )
            elif response.status_code == 404:
                message = response_json.get("message", "")
                raise TradeXDataFetchError(f"{message if message else ''} for endpoint: {endpoint}")

        except requests.exceptions.JSONDecodeError:
            raise TradeXAPIError(f"Invalid JSON response from {endpoint}. Response: {response.text}")
        except Exception as ex:
            raise TradeXAPIError(f"An unknown error occurred for endpoint {endpoint}: {ex}")

    def start_websocket(self, auto_reconnect=True):
        """
        Start the websocket connection
        
        Args:
            auto_reconnect (bool): Whether to automatically reconnect if connection drops
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if self.websocket_running:
            return True
            
        if self.token:
            self.websocket_client = TradeXWebSocketClient(self.websocket_host, self.websocket_port, self.token, self.client_id, 3, 3)
            if self.websocket_client.start():
                self.websocket_running = True
                return True
            else:
                return False
        else:
            print("Please Login First!")
        return False

    def stop_websocket(self):
        """
        Stop the websocket connection
        
        Returns:
            bool: True if successfully stopped or not running, False otherwise
        """
        if not self.websocket_running:
            return True
            
        self.websocket_client.stop()
        self.websocket_running = False
        return True
    
    def register_callback(self, message_type, callback_function):
        """
        Register a callback function for a specific message type
        
        Args:
            message_type (str): The type of message to listen for
            callback_function (function): The function to call when the message is received
        """
        if self.websocket_client:
            self.websocket_client.register_callback(message_type, callback_function)
        else:
            raise TradeXAPIError("Websocket client is not initialized. Please start the websocket first.")