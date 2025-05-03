import os
import time
import random
import string
import socket
import ssl
import json
import struct
import threading
import base64
import hashlib

from .models import OrderBookData, TradesBookData

class TradeXWebSocketClient:
    def __init__(self, host, port, token, client_id, reconnect_attempts=5, reconnect_delay=3):
        self.websocket_host = host
        self.websocket_port = port
        self.token = token
        self.client_id = client_id
        self.websocket_magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        self.is_running = False
        self.client_socket = None
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.connection_lock = threading.Lock()
        self.receiver_thread = None
        self.reconnecting = False
        self.callbacks = {}
        self.last_ping_time = 0
        self.ping_interval = 30
        
        print(self.token)

    def start(self):
        self.is_running = True
        return self._connect_with_retry()

    def register_callback(self, message_type, callback_function):
        """
        Register a callback function for a specific message type
        
        Args:
            message_type (str): Type of message to listen for 
            callback_function (callable): Function to call when message received
        """
        self.callbacks[message_type] = callback_function

    def stop(self):
        self.is_running = False
        with self.connection_lock:
            if self.client_socket:
                try:
                    close_frame = struct.pack("B", 0x88) + struct.pack("B", 0)
                    self.client_socket.send(close_frame)
                except:
                    pass
                finally:
                    try:
                        self.client_socket.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    self.client_socket.close()
                    self.client_socket = None
        print("[STOPPED] WebSocket client stopped.")

    def _connect_with_retry(self):
        attempt = 0
        connected = False
        self.reconnecting = True
        
        # Exponential backoff for reconnection
        delay = self.reconnect_delay
        
        while self.is_running and attempt < self.reconnect_attempts and not connected:
            if attempt > 0:
                print(f"[RECONNECTING] Reconnection attempt {attempt}/{self.reconnect_attempts} in {delay} seconds...")
                time.sleep(delay)
                # Increase delay for next attempt (exponential backoff)
                delay = min(delay * 2, 30)  # Cap at 30 seconds
                
            try:
                connected = self._connect_websocket()
            except Exception as e:
                print(f"[ERROR] Connection attempt failed: {e}")
            attempt += 1
            
        self.reconnecting = False
        if not connected and self.is_running:
            print("[ERROR] Failed to connect after multiple attempts. Giving up.")
            self.is_running = False
        return connected

    def _connect_websocket(self):
        websocket_key = self._generate_websocket_key()
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.settimeout(30)  # More reasonable timeout
        
        context = ssl.create_default_context()
        client_socket = context.wrap_socket(raw_socket, server_hostname=self.websocket_host)
        
        try:
            client_socket.connect((self.websocket_host, self.websocket_port))
            print("[SUCCESS] Connected to WebSocket server!")
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            try:
                client_socket.close()
            except:
                pass
            return False
            
        if not self._perform_handshake(client_socket, websocket_key):
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            client_socket.close()
            return False
            
        with self.connection_lock:
            self.client_socket = client_socket
            
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        # Start receiver thread
        self.receiver_thread = threading.Thread(target=self._receive_messages, daemon=True)
        self.receiver_thread.start()
        
        return True

    def _perform_handshake(self, client_socket, websocket_key):
        handshake_request = (
            f"GET /?token={self.token}&clientID={self.client_id} HTTP/1.1\r\n"
            f"Host: {self.websocket_host}:{self.websocket_port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {websocket_key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"Origin: http://{self.websocket_host}\r\n"
            f"\r\n"
        )
        
        client_socket.send(handshake_request.encode())
        
        # Improved handshake response handling
        response_buffer = bytearray()
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 second timeout for handshake
            try:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_buffer.extend(chunk)
                
                # Check if we've received the end of the headers
                if b"\r\n\r\n" in response_buffer:
                    break
            except socket.timeout:
                continue
                
        if not response_buffer:
            print("[ERROR] No handshake response received.")
            return False
            
        response = response_buffer.decode(errors="ignore")
        expected_accept_key = self._generate_accept_key(websocket_key)
        
        # Check for HTTP 101 status and accept key
        if "HTTP/1.1 101" not in response or expected_accept_key.lower() not in response.lower():
            print("[ERROR] WebSocket handshake failed.")
            print("[SERVER] Server Response:\n", response)
            return False
            
        print("[SUCCESS] WebSocket connection established successfully!")
        return True

    def _generate_websocket_key(self):
        key = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        return base64.b64encode(key.encode()).decode()

    def _generate_accept_key(self, key):
        hash_value = hashlib.sha1((key + self.websocket_magic_string).encode()).digest()
        return base64.b64encode(hash_value).decode()

    def _heartbeat_loop(self):
        """Send periodic pings to keep the connection alive"""
        while self.is_running:
            current_time = time.time()
            if current_time - self.last_ping_time > self.ping_interval:
                self.last_ping_time = current_time
                self._send_ping()
            time.sleep(1)
    
    def _send_ping(self):
        """Send a ping control frame to the server"""
        with self.connection_lock:
            if self.client_socket:
                try:
                    ping_frame = struct.pack("B", 0x89) + struct.pack("B", 0)
                    self.client_socket.send(ping_frame)
                    print("[PING] Sent ping to server")
                except Exception as e:
                    print(f"[ERROR] Failed to send ping: {e}")
                    self._handle_connection_failure()

    def send_message(self, message):
        with self.connection_lock:
            if not self.client_socket:
                print("[ERROR] Not connected. Cannot send message.")
                return False
            try:
                self._send_websocket_message(self.client_socket, message)
                print(f"[SENT] Sent message: {message}")
                return True
            except Exception as e:
                print(f"[ERROR] Error sending message: {e}")
                self._handle_connection_failure()
                return False

    def _send_websocket_message(self, client_socket, message):
        message_bytes = message.encode("utf-8", errors="replace")
        message_length = len(message_bytes)
        masking_key = os.urandom(4)
        masked_message = bytearray(b ^ masking_key[i % 4] for i, b in enumerate(message_bytes))
        
        if message_length < 126:
            frame = struct.pack("B", 0x81) + struct.pack("B", 0x80 | message_length) + masking_key
        elif message_length < 65536:
            frame = struct.pack("B", 0x81) + struct.pack("B", 0x80 | 126) + struct.pack(">H", message_length) + masking_key
        else:
            frame = struct.pack("B", 0x81) + struct.pack("B", 0x80 | 127) + struct.pack(">Q", message_length) + masking_key
            
        client_socket.send(frame + masked_message)

    def _receive_messages(self):
        connection_error = False
        
        while self.is_running:
            with self.connection_lock:
                if not self.client_socket:
                    time.sleep(0.1)
                    continue
                socket_ref = self.client_socket
                
            try:
                if connection_error:
                    # If we had a connection error before, check socket health
                    socket_ref.settimeout(1)
                    socket_ref.send(struct.pack("B", 0x89) + struct.pack("B", 0))  # Send ping
                    connection_error = False
                    socket_ref.settimeout(1)  # Short timeout for active reading
                
                self._process_messages(socket_ref)
            except socket.timeout:
                # Timeout is expected, just continue
                pass
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[WARNING] Connection problem: {e}")
                connection_error = True
                if self.is_running:
                    self._handle_connection_failure()
            except Exception as e:
                print(f"[WARNING] Receiver error: {e}")
                connection_error = True
                if self.is_running:
                    self._handle_connection_failure()
                    
            time.sleep(0.01)  # Small sleep to prevent CPU spike
            
        print("[INFO] Receiver thread terminated.")

    def _handle_connection_failure(self):
        if self.reconnecting:
            return
            
        print("[INFO] Connection lost. Attempting to reconnect...")
        
        with self.connection_lock:
            if self.client_socket:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
                
        if self.is_running:
            # Use a separate thread for reconnection to avoid blocking
            reconnect_thread = threading.Thread(target=self._connect_with_retry, daemon=True)
            reconnect_thread.start()

    def _process_messages(self, client_socket):
        """Process incoming WebSocket messages"""
        buffer = bytearray()
        frame_buffer = bytearray()
        is_fragmented = False
        
        # Set socket to non-blocking with a reasonable timeout
        client_socket.settimeout(1)
        
        # Process messages until timeout or error
        while self.is_running:
            try:
                # Read header (2 bytes minimum)
                header = self._read_exactly(client_socket, 2)
                if not header or len(header) < 2:
                    # Could be a timeout, which is normal
                    return
                
                first_byte, second_byte = header[0], header[1]
                fin = (first_byte & 0x80) >> 7
                opcode = first_byte & 0x0F
                masked = (second_byte & 0x80) >> 7
                payload_length = second_byte & 0x7F
                
                # Handle control frames immediately
                if opcode == 8:  # Close frame
                    print("[INFO] WebSocket connection closed by server.")
                    self._handle_connection_failure()
                    return
                elif opcode == 9:  # Ping
                    # Respond with pong
                    pong_frame = struct.pack("B", 0x8A) + struct.pack("B", 0)
                    client_socket.send(pong_frame)
                    continue
                elif opcode == 10:  # Pong
                    print("[PONG] Received pong from server")
                    continue
                
                # Read extended payload length if needed
                if payload_length == 126:
                    ext_length = self._read_exactly(client_socket, 2)
                    if not ext_length or len(ext_length) < 2:
                        return
                    payload_length = struct.unpack(">H", ext_length)[0]
                elif payload_length == 127:
                    ext_length = self._read_exactly(client_socket, 8)
                    if not ext_length or len(ext_length) < 8:
                        return
                    payload_length = struct.unpack(">Q", ext_length)[0]
                
                # Read masking key if present
                mask = None
                if masked:
                    mask = self._read_exactly(client_socket, 4)
                    if not mask or len(mask) < 4:
                        return
                
                # Read payload data
                if payload_length > 0:
                    payload_data = self._read_exactly(client_socket, payload_length)
                    if not payload_data or len(payload_data) != payload_length:
                        print(f"[ERROR] Incomplete message received. Got {len(payload_data) if payload_data else 0}, expected {payload_length}")
                        return
                    
                    # Unmask data if needed
                    if masked and mask:
                        payload_data = bytearray(payload_data[i] ^ mask[i % 4] for i in range(payload_length))
                    
                    # Continuation frame or new message
                    if opcode == 0:  # Continuation frame
                        frame_buffer.extend(payload_data)
                    elif opcode == 1:  # Text frame
                        if is_fragmented:
                            print("[WARNING] Received new text frame while processing fragmented message")
                            frame_buffer.clear()
                        frame_buffer.extend(payload_data)
                        is_fragmented = not fin
                    elif opcode == 2:  # Binary frame
                        if is_fragmented:
                            print("[WARNING] Received new binary frame while processing fragmented message")
                            frame_buffer.clear()
                        frame_buffer.extend(payload_data)
                        is_fragmented = not fin
                
                # Process complete message if FIN bit is set
                if fin and frame_buffer:
                    try:
                        decoded_message = frame_buffer.decode("utf-8", errors="replace")
                        try:
                            json_data = json.loads(decoded_message)
                            
                            # Extract the message type from the top level
                            message_type = json_data.get("eventType")
                            print(f"[RECEIVED] Event type: {message_type}")
                            
                            data = json_data
                            
                            if message_type == "order":
                                data = OrderBookData(**json_data.get("data", {}))
                            elif message_type == "trade":
                                data = TradesBookData(**json_data.get("data", {}))
                            
                            # Process callbacks in a separate thread to avoid blocking the receiver
                            if message_type and message_type in self.callbacks:
                                callback_thread = threading.Thread(
                                    target=self._execute_callback,
                                    args=(message_type, data),
                                    daemon=True
                                )
                                callback_thread.start()
                            else:
                                print(f"[INFO] No callback registered for event type: {message_type}")
                                
                        except json.JSONDecodeError:
                            print(f"[RECEIVED] Received non-JSON message: {decoded_message[:100]}...")
                    except UnicodeDecodeError:
                        print("[WARNING] Received binary data, not displaying")
                    finally:
                        frame_buffer.clear()
                        is_fragmented = False
                        
            except socket.timeout:
                # Timeout is normal for non-blocking operation
                return
            except Exception as e:
                print(f"[WARNING] Error processing message: {e}")
                return

    def _execute_callback(self, message_type, data):
        """Execute callback in a separate thread"""
        try:
            self.callbacks[message_type](data)
        except Exception as e:
            print(f"[ERROR] Callback execution failed for {message_type}: {e}")

    def _read_exactly(self, sock, n):
        """Read exactly n bytes from the socket"""
        if n <= 0:
            return bytearray()
        
        data = bytearray()
        remaining = n
        
        # Use the socket's current timeout
        start_time = time.time()
        timeout = sock.gettimeout() or 30
        
        while remaining > 0 and (time.time() - start_time) < timeout:
            try:
                chunk = sock.recv(remaining)
                if not chunk:  # Connection closed
                    return None
                data.extend(chunk)
                remaining -= len(chunk)
                
                if remaining == 0:
                    return data
                    
            except socket.timeout:
                # Check if we should continue waiting
                if not self.is_running:
                    return None
                # Raise timeout if we've exceeded our limit
                if (time.time() - start_time) >= timeout:
                    raise socket.timeout("Timed out waiting for data")
            
        # If we got here without returning, we didn't get all the data
        if remaining > 0:
            return None
            
        return data