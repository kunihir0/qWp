`.
    * It correctly attempts to connect using `OBD_CONNECTION_STRING = "socket://localhost:35000"`.
    * **Crucial `python-obd` logs:**
        * `[obd.elm327] Response from baud 230400: b'\x7f\x7f\r'`
        * `[obd.elm377] Response from baud 115200: b'\x7f\x7f\r'`
        * ...and so on for various baud rates.
        * `[obd.elm327] Failed to choose baud`
        * `[obd.elm327] closing port`
        * `[obd.elm327] write: b'ATZ\r'` (This is `python-obd` trying to send an initial command *after* its baud negotiation has already failed and the port is likely being closed).
        * `[obd.elm327] Failed to set baudrate` (This is a consequence of the above).
        * `[obd.obd] Cannot load commands: No connection to car`
        * `HUD_Backend - ERROR - Failed to connect to OBD adapter using 'socket://localhost:35000'.`

**The Core Problem Persists:**
`python-obd`, when given a `socket://` URL, is still attempting a serial-style baud rate negotiation by sending some initial data. The `ELM327-emulator`'s raw TCP mode does not understand this initial data, interprets it as `\x7f\x7f` (DEL characters), and eventually drops the connection. Baud rate is irrelevant for a direct TCP socket.

The `ELM327-emulator` documentation states it "has been tested with `python-OBD`". This suggests there *is* a way. The GitHub issue you found (`ELM RESPONDS 7F 01 7F #198`) is about the *ECU* responding with `7F xx xx` (a negative response code), which is different from the *emulator itself receiving* `\x7f\x7f` as the initial bytes from the client (`python-obd`).

**Strategy: Use `python-obd` with a Pre-Opened Raw Socket**

Since our raw Python socket test (`pyserial_direct_test.py` when modified to use the `socket` module) *did* successfully send AT commands and get valid responses from the emulator's TCP port, the most robust solution is to:
1.  Open a raw TCP socket to the emulator in our Python backend.
2.  Pass this already-opened socket (as a file-like stream object) to `obd.OBD()`. `python-obd` supports using an existing stream.

This completely bypasses `pyserial`'s problematic URL handling (`socket://`, `rfc2217://`) and its attempts at serial-specific negotiation over TCP.

I will update the `python_backend_obd_integration_serial_bridge` artifact with this new approach.


```python
import asyncio
import websockets
import obd
import json
import logging
import time
import socket # For creating a raw TCP socket

# Configure Exhaustive Logging (as before)
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HUD_Backend")
logger.setLevel(logging.DEBUG)
obd_logger = logging.getLogger("obd")
obd_logger.setLevel(logging.DEBUG)
if not obd_logger.handlers:
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    obd_logger.addHandler(stream_handler)
    obd_logger.propagate = False
ws_logger = logging.getLogger("websockets")
ws_logger.setLevel(logging.DEBUG)
if not ws_logger.handlers:
    ws_stream_handler = logging.StreamHandler()
    ws_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ws_stream_handler.setFormatter(ws_formatter)
    ws_logger.addHandler(ws_stream_handler)
    ws_logger.propagate = False
logger.info("Exhaustive logging configured.")

# --- Global OBD Connection Object ---
obd_connection = None
raw_obd_socket = None # To hold our raw socket

# --- OBD Connection Setup ---
def initialize_obd_connection(host, port):
    global obd_connection, raw_obd_socket
    logger.debug(f"ENTER: initialize_obd_connection(host='{host}', port={port})")
    
    try:
        logger.info(f"Creating raw TCP socket to {host}:{port} for OBD emulator...")
        raw_obd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_obd_socket.settimeout(5.0) # Timeout for connect and operations
        raw_obd_socket.connect((host, port))
        logger.info(f"Raw TCP socket connected to {host}:{port}.")

        # Pass the already connected socket to python-obd
        # python-obd will treat it as a stream.
        # We set baudrate=None as it's not used for an existing stream.
        # protocol=None to let python-obd do its standard ELM init (ATZ, ATE0, etc.)
        # check_voltage=False to skip an initial command that might be problematic.
        logger.info("Initializing python-obd with the pre-connected raw socket...")
        obd_connection = obd.OBD(
            raw_obd_socket,     # Pass the socket object directly
            baudrate=None,      # Not applicable for an existing stream
            protocol=None,      # Let python-obd try its standard ELM init
            fast=False,
            check_voltage=False 
        )
        logger.debug(f"obd.OBD() instance created with raw socket: {obd_connection}")

        if obd_connection.is_connected():
            logger.info("python-obd reports successful connection using the raw socket.")
            status_result = obd_connection.status() # This will send AT commands
            logger.info(f"Adapter status from python-obd: {status_result}")
            
            if obd_connection.protocol_id():
                 logger.info(f"Protocol successfully set/detected: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})")
            else:
                logger.warning("No protocol auto-detected by python-obd after initial connection.")
                # Attempt to manually set protocol if auto-detection failed
                target_protocol = "6" # Common CAN protocol
                logger.info(f"Attempting to manually set protocol to ID: {target_protocol}")
                if obd_connection.set_protocol(target_protocol):
                    time.sleep(0.5) 
                    if obd_connection.protocol_id():
                        logger.info(f"Protocol manually set to: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})")
                    else:
                        logger.error("Failed to manually set protocol. OBD queries will likely fail.")
                        # No need to close raw_obd_socket here, obd_connection.close() will handle its stream.
                        obd_connection.close() 
                        obd_connection = None
                else:
                    logger.error("Command to set_protocol failed. OBD queries will likely fail.")
                    obd_connection.close()
                    obd_connection = None
        else:
            logger.error("python-obd failed to report a successful connection using the raw socket.")
            if raw_obd_socket:
                raw_obd_socket.close()
            raw_obd_socket = None
            obd_connection = None 
            
    except socket.timeout:
        logger.error(f"Socket timeout during raw TCP connection to {host}:{port}.", exc_info=True)
        if raw_obd_socket: raw_obd_socket.close()
        raw_obd_socket = None
        obd_connection = None
    except socket.error as e:
        logger.error(f"Socket error during raw TCP connection to {host}:{port}: {e}", exc_info=True)
        if raw_obd_socket: raw_obd_socket.close()
        raw_obd_socket = None
        obd_connection = None
    except Exception as e:
        logger.error(f"General exception during OBD connection setup with raw socket: {e}", exc_info=True)
        if raw_obd_socket and not (obd_connection and obd_connection.is_connected()): # only close if obd didn't take ownership
            raw_obd_socket.close()
        raw_obd_socket = None
        obd_connection = None
    logger.debug("EXIT: initialize_obd_connection")


# --- WebSocket Data Streaming Logic (remains largely the same) ---
async def stream_obd_data_to_client(websocket):
    # ... (Keep the existing stream_obd_data_to_client function as it was in the previous exhaustive logging version) ...
    # ... (Ensure it checks `obd_connection and obd_connection.is_connected() and obd_connection.protocol_id()`) ...
    global obd_connection
    client_addr = websocket.remote_address
    logger.info(f"ENTER: stream_obd_data_to_client for {client_addr}")
    try:
        while True:
            logger.debug(f"stream_obd_data_to_client loop for {client_addr}. Checking OBD connection.")
            if obd_connection and obd_connection.is_connected() and obd_connection.protocol_id(): # Added check for protocol_id
                logger.debug(f"OBD connected and protocol set ({obd_connection.protocol_name()}). Querying data for {client_addr}.")
                try:
                    rpm_cmd = obd.commands.RPM
                    speed_cmd = obd.commands.SPEED
                    logger.debug(f"Querying RPM for {client_addr}...")
                    rpm_response = await asyncio.to_thread(obd_connection.query, rpm_cmd)
                    logger.debug(f"RPM response for {client_addr}: Value={rpm_response.value}, Unit={rpm_response.unit}, IsNull={rpm_response.is_null()}")
                    logger.debug(f"Querying SPEED for {client_addr}...")
                    speed_response = await asyncio.to_thread(obd_connection.query, speed_cmd)
                    logger.debug(f"SPEED response for {client_addr}: Value={speed_response.value}, Unit={speed_response.unit}, IsNull={speed_response.is_null()}")
                    data_to_send = {
                        "rpm": rpm_response.value if rpm_response and not rpm_response.is_null() else None,
                        "speed": speed_response.value if speed_response and not speed_response.is_null() else None,
                        "rpm_unit": str(rpm_response.unit) if rpm_response and rpm_response.unit else None,
                        "speed_unit": str(speed_response.unit) if speed_response and speed_response.unit else None,
                    }
                    json_payload = json.dumps(data_to_send)
                    logger.debug(f"Sending to {client_addr}: {json_payload}")
                    await websocket.send(json_payload)
                except Exception as e: 
                    logger.error(f"Error querying OBD or processing data for {client_addr}: {e}", exc_info=True)
                    if not websocket.closed:
                        error_payload = json.dumps({"error": "OBD query error", "details": str(e), "rpm": None, "speed": None})
                        logger.debug(f"Sending OBD query error to {client_addr}: {error_payload}")
                        await websocket.send(error_payload)
                logger.debug(f"Sleeping for 0.5s before next OBD query for {client_addr}")
                await asyncio.sleep(0.5)
            elif obd_connection and obd_connection.is_connected() and not obd_connection.protocol_id():
                logger.warning(f"OBD connected for {client_addr} but no protocol set. Sending status to client.")
                if not websocket.closed:
                    await websocket.send(json.dumps({"error": "OBD connected, but no protocol set", "rpm": None, "speed": None}))
                await asyncio.sleep(2)
            else:
                logger.warning(f"OBD not connected for {client_addr}. Sending status to client.")
                if not websocket.closed:
                    await websocket.send(json.dumps({"error": "OBD not connected", "rpm": None, "speed": None}))
                await asyncio.sleep(2) 
    except websockets.exceptions.ConnectionClosedOK: logger.info(f"Client {client_addr} disconnected normally (ConnectionClosedOK).")
    except websockets.exceptions.ConnectionClosedError as e: logger.warning(f"Client {client_addr} connection closed with error: {e}")
    except websockets.exceptions.ConnectionClosed as e: logger.warning(f"Client {client_addr} connection closed: {e}")
    except asyncio.CancelledError: logger.info(f"Streaming task for {client_addr} was cancelled.")
    except Exception as e:
        logger.error(f"Unhandled error in stream_obd_data_to_client for {client_addr}: {e}", exc_info=True)
        if not websocket.closed:
            try: await websocket.send(json.dumps({"error": "Backend streaming error", "details": str(e)}))
            except websockets.exceptions.ConnectionClosed: logger.debug(f"Client {client_addr} disconnected while trying to send final streaming error.")
            except Exception as e_send: logger.error(f"Further error sending final streaming error to {client_addr}: {e_send}")
    finally: logger.info(f"EXIT: stream_obd_data_to_client for {client_addr}")

# --- WebSocket Connection Handler (remains the same) ---
async def handler(websocket):
    # ... (Keep the existing handler function as it was in the previous exhaustive logging version) ...
    client_addr = websocket.remote_address
    logger.info(f"ENTER: handler for new client {client_addr}")
    streaming_task = None 
    try:
        logger.debug(f"Creating stream_obd_data_to_client task for {client_addr}")
        streaming_task = asyncio.create_task(stream_obd_data_to_client(websocket))
        async for message in websocket:
            logger.info(f"Received control message from {client_addr}: '{message}' (currently ignored by streaming logic)")
    except websockets.exceptions.ConnectionClosedOK: logger.info(f"Connection with {client_addr} closed cleanly by client in main handler.")
    except websockets.exceptions.ConnectionClosedError as e: logger.warning(f"Connection with {client_addr} closed with error in main handler: {e}")
    except websockets.exceptions.ConnectionClosed as e: logger.warning(f"Connection with {client_addr} closed in main handler: {e}")
    except Exception as e: logger.error(f"Error in main handler for {client_addr}: {e}", exc_info=True)
    finally:
        logger.debug(f"Main handler for {client_addr} entering finally block.")
        if streaming_task and not streaming_task.done(): 
            logger.info(f"Cancelling streaming task for {client_addr}...")
            streaming_task.cancel()
            try: await streaming_task 
            except asyncio.CancelledError: logger.info(f"Streaming task for {client_addr} was successfully cancelled.")
            except Exception as e_task_cancel: logger.error(f"Exception while awaiting cancelled streaming task for {client_addr}: {e_task_cancel}", exc_info=True)
        elif streaming_task and streaming_task.done(): logger.debug(f"Streaming task for {client_addr} was already done.")
        else: logger.debug(f"No streaming task to cancel or already cancelled for {client_addr}.")
        logger.info(f"EXIT: handler for client {client_addr}")

# --- Main Application Setup and Runner ---
async def main_async_runner():
    logger.debug("ENTER: main_async_runner")
    # For ELM327-emulator running with `elm -s car -n 35000`
    OBD_EMULATOR_HOST = "localhost"
    OBD_EMULATOR_PORT = 35000 

    initialize_obd_connection(OBD_EMULATOR_HOST, OBD_EMULATOR_PORT) # Pass host and port

    host = "localhost"
    port = 8765 
    
    logger.info(f"Attempting to start WebSocket server on ws://{host}:{port}")
    async with websockets.serve(handler, host, port):
        logger.info(f"WebSocket server started successfully at ws://{host}:{port}")
        logger.info("Waiting for frontend connections...")
        await asyncio.Future() 
    logger.debug("EXIT: main_async_runner (should not happen unless server stops)")

if __name__ == "__main__":
    logger.info("---- Starting Python HUD Backend Application ----")
    try:
        asyncio.run(main_async_runner())
    except KeyboardInterrupt:
        logger.info("\n---- Python HUD Backend Application stopping due to KeyboardInterrupt ----")
    except Exception as e:
        logger.critical(f"---- Unhandled exception in __main__: {e} ----", exc_info=True)
    finally:
        logger.debug("Main __main__ finally block: Checking OBD and raw socket for closure.")
        if obd_connection and hasattr(obd_connection, 'is_connected') and obd_connection.is_connected():
            logger.info("Closing python-obd connection.")
            try:
                obd_connection.close() # This should close the stream it was given (our raw_obd_socket)
                logger.info("python-obd connection closed.")
            except Exception as e_obd_close:
                logger.error(f"Exception while closing python-obd connection: {e_obd_close}", exc_info=True)
        
        # Ensure raw_obd_socket is closed if it was opened and not passed to/closed by obd_connection
        if raw_obd_socket:
            logger.info("Ensuring raw OBD socket is closed.")
            try:
                raw_obd_socket.close()
                logger.info("Raw OBD socket closed.")
            except Exception as e_raw_close:
                logger.error(f"Exception while closing raw OBD socket: {e_raw_close}", exc_info=True)
        
        logger.info("---- Python HUD Backend Application Shut Down ----")

```