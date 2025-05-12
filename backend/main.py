import asyncio
import websockets
import obd
import json
import logging
import time
import socket  # For creating a raw TCP socket
from pint import Quantity

# Configure Exhaustive Logging (as before)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("HUD_Backend")
logger.setLevel(logging.DEBUG)
obd_logger = logging.getLogger("obd")
obd_logger.setLevel(logging.DEBUG)
if not obd_logger.handlers:
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)
    obd_logger.addHandler(stream_handler)
    obd_logger.propagate = False
ws_logger = logging.getLogger("websockets")
ws_logger.setLevel(logging.DEBUG)
if not ws_logger.handlers:
    ws_stream_handler = logging.StreamHandler()
    ws_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ws_stream_handler.setFormatter(ws_formatter)
    ws_logger.addHandler(ws_stream_handler)
    ws_logger.propagate = False
logger.info("Exhaustive logging configured.")

# --- Global OBD Connection Object ---
obd_connection = None


# --- OBD Connection Setup ---
def initialize_obd_connection(host, port):
    global obd_connection
    logger.debug(f"ENTER: initialize_obd_connection(host='{host}', port={port})")

    try:
        # python-obd will handle the socket creation and connection internally
        # when given a "socket://" connection string.
        # We set baudrate to a specific value for socket connections to prevent
        # problematic auto-baud detection by some python-obd versions.
        # protocol=None lets python-obd do its standard ELM init (ATZ, ATE0, etc.)
        # check_voltage=False skips an initial command that might be problematic.
        connection_string = f"socket://{host}:{port}"
        logger.info(f"Initializing python-obd with connection string: {connection_string}")
        obd_connection = obd.OBD(
            connection_string,
            baudrate=38400,
            protocol=None,
            fast=False,
            check_voltage=False,
        )
        logger.debug(f"obd.OBD() instance created: {obd_connection}")

        if obd_connection.is_connected():
            logger.info(
                "python-obd reports successful connection."
            )
            status_result = obd_connection.status()  # This will send AT commands
            logger.info(f"Adapter status from python-obd: {status_result}")

            if obd_connection.protocol_id():
                logger.info(
                    f"Protocol successfully set/detected: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})"
                )
            else:
                logger.warning(
                    "No protocol auto-detected by python-obd after initial connection."
                )
                # Attempt to manually set protocol if auto-detection failed
                target_protocol = "6"  # Common CAN protocol
                logger.info(
                    f"Attempting to manually set protocol to ID: {target_protocol}"
                )
                if obd_connection.set_protocol(target_protocol):
                    time.sleep(0.5)
                    if obd_connection.protocol_id():
                        logger.info(
                            f"Protocol manually set to: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})"
                        )
                    else:
                        logger.error(
                            "Failed to manually set protocol. OBD queries will likely fail."
                        )
                        obd_connection.close()
                        obd_connection = None
                else:
                    logger.error(
                        "Command to set_protocol failed. OBD queries will likely fail."
                    )
                    obd_connection.close()
                    obd_connection = None
        else:
            logger.error(
                "python-obd failed to report a successful connection."
            )
            obd_connection = None

    except socket.timeout: # This might still be relevant if python-obd raises it
        logger.error(
            f"Socket timeout during OBD connection to {host}:{port}.", exc_info=True
        )
        obd_connection = None
    except socket.error as e: # This might still be relevant if python-obd raises it
        logger.error(
            f"Socket error during OBD connection to {host}:{port}: {e}",
            exc_info=True,
        )
        obd_connection = None
    except Exception as e:
        logger.error(
            f"General exception during OBD connection setup: {e}",
            exc_info=True,
        )
        obd_connection = None
    logger.debug("EXIT: initialize_obd_connection")


# --- WebSocket Data Streaming Logic (remains largely the same) ---
async def stream_obd_data_to_client(websocket):
    # ... (Keep the existing stream_obd_data_to_client function as it was in the previous exhaustive logging version) ...
    # ... (Ensure it checks `obd_connection and obd_connection.is_connected() and obd_connection.protocol_id()`) ...
        client_addr = websocket.remote_address
        logger.info(f"ENTER: stream_obd_data_to_client for {client_addr}")
    
        # Simulator state variables
        # OBD Polling Interval
        OBD_POLLING_INTERVAL = 0.2  # seconds, configurable as per future considerations
        # Initialize variables for storing OBD data, will persist across loop iterations
        current_rpm = 0.0
        current_speed_mph = 0.0
    
        try:
            while True:
                logger.debug(
                    f"OBD: stream_obd_data_to_client loop for {client_addr}. Querying OBD."
                )

                data_status = "OK" # Default status for this cycle

                if obd_connection and obd_connection.is_connected() and obd_connection.protocol_id():
                    # Query RPM
                    rpm_response = obd_connection.query(obd.commands.RPM)
                    if not rpm_response.is_null() and rpm_response.value is not None:
                        # Assuming rpm_response.value is a pint.Quantity
                        current_rpm = round(rpm_response.value.magnitude, 2)
                    else:
                        # Keep last known current_rpm or its initial 0.0 value
                        data_status = "RPM_ERROR"
                        logger.warning(f"OBD: Failed to retrieve RPM or RPM is null for {client_addr}. Using last known/default value: {current_rpm}")

                    # Query Speed
                    speed_response = obd_connection.query(obd.commands.SPEED)
                    current_speed_kmph = 0.0 # Initialize for current scope, will be basis for current_speed_mph
                    if not speed_response.is_null() and speed_response.value is not None:
                        # Assuming speed_response.value is a pint.Quantity in KMPH
                        current_speed_kmph = speed_response.value.magnitude
                    else:
                        # Keep last known current_speed_mph (derived from kmph) or its initial 0.0 value
                        # by not re-calculating it from a new (failed) kmph reading.
                        # Update status accordingly.
                        new_speed_status = "SPEED_ERROR"
                        if data_status == "RPM_ERROR": # RPM already failed in this cycle
                            data_status = "RPM_SPEED_ERROR"
                        else: # RPM was OK or this is the first error in this cycle
                            data_status = new_speed_status
                        logger.warning(f"OBD: Failed to retrieve Speed or Speed is null for {client_addr}. Speed KMPH basis remains {current_speed_kmph}, MPH: {current_speed_mph}")
                    
                    # Convert KMPH to MPH only if speed was successfully queried or to re-affirm 0 if it failed
                    conversion_factor_kmph_to_mph = 0.621371
                    current_speed_mph = round(current_speed_kmph * conversion_factor_kmph_to_mph, 2)

                else:
                    logger.warning(
                        f"OBD: Not connected or protocol not set for {client_addr}. Sending default error data."
                    )
                    # Reset to 0 to clearly indicate no live data when OBD is disconnected
                    current_rpm = 0.0
                    current_speed_mph = 0.0
                    data_status = "OBD_DISCONNECTED"
                    # Add a longer sleep here to prevent busy-looping if OBD is down
                    logger.debug(f"OBD: Connection issue for {client_addr}. Sleeping for 2s before next check in loop.")
                    await asyncio.sleep(2.0) # Wait longer before retrying connection check in the next loop iteration

                data_to_send = {
                    "rpm": current_rpm,
                    "rpm_unit": "rpm",
                    "speed": current_speed_mph,
                    "speed_unit": "MPH",
                    "status": data_status
                }
                json_payload = json.dumps(data_to_send)
                logger.debug(f"OBD: Sending to {client_addr}: {json_payload}")
                await websocket.send(json_payload)
                
                # If OBD was disconnected, we already slept for 2s.
                # Otherwise, sleep for the normal polling interval.
                if data_status != "OBD_DISCONNECTED":
                    logger.debug(
                        f"OBD: Sleeping for {OBD_POLLING_INTERVAL}s before next OBD query for {client_addr}"
                    )
                    await asyncio.sleep(OBD_POLLING_INTERVAL)
    
        except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"Client {client_addr} disconnected normally (ConnectionClosedOK).")
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"Client {client_addr} connection closed with error: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"Client {client_addr} connection closed: {e}")
        except asyncio.CancelledError:
            logger.info(f"Streaming task for {client_addr} was cancelled.")
        except Exception as e:
            logger.error(
                f"Unhandled error in stream_obd_data_to_client for {client_addr}: {e}",
                exc_info=True,
            )
            if websocket.state != 3: # 3 typically means ConnectionState.CLOSED
                try:
                    await websocket.send(
                        json.dumps({"error": "Backend streaming error", "details": str(e)})
                    )
                except websockets.exceptions.ConnectionClosed:
                    logger.debug(
                        f"Client {client_addr} disconnected while trying to send final streaming error."
                    )
                except Exception as e_send:
                    logger.error(
                        f"Further error sending final streaming error to {client_addr}: {e_send}"
                    )
        finally:
            logger.info(f"EXIT: stream_obd_data_to_client for {client_addr}")


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
            logger.info(
                f"Received control message from {client_addr}: '{message}' (currently ignored by streaming logic)"
            )
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(
            f"Connection with {client_addr} closed cleanly by client in main handler."
        )
    except websockets.exceptions.ConnectionClosedError as e:
        logger.warning(
            f"Connection with {client_addr} closed with error in main handler: {e}"
        )
    except websockets.exceptions.ConnectionClosed as e:
        logger.warning(f"Connection with {client_addr} closed in main handler: {e}")
    except Exception as e:
        logger.error(f"Error in main handler for {client_addr}: {e}", exc_info=True)
    finally:
        logger.debug(f"Main handler for {client_addr} entering finally block.")
        if streaming_task and not streaming_task.done():
            logger.info(f"Cancelling streaming task for {client_addr}...")
            streaming_task.cancel()
            try:
                await streaming_task
            except asyncio.CancelledError:
                logger.info(
                    f"Streaming task for {client_addr} was successfully cancelled."
                )
            except Exception as e_task_cancel:
                logger.error(
                    f"Exception while awaiting cancelled streaming task for {client_addr}: {e_task_cancel}",
                    exc_info=True,
                )
        elif streaming_task and streaming_task.done():
            logger.debug(f"Streaming task for {client_addr} was already done.")
        else:
            logger.debug(
                f"No streaming task to cancel or already cancelled for {client_addr}."
            )
        logger.info(f"EXIT: handler for client {client_addr}")


# --- Main Application Setup and Runner ---
async def main_async_runner():
    logger.debug("ENTER: main_async_runner")
    # For ELM327-emulator running with `elm -s car -n 35000`
    OBD_EMULATOR_HOST = "localhost"
    OBD_EMULATOR_PORT = 35000

    initialize_obd_connection(
        OBD_EMULATOR_HOST, OBD_EMULATOR_PORT
    )  # Pass host and port

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
        logger.info(
            "\n---- Python HUD Backend Application stopping due to KeyboardInterrupt ----"
        )
    except Exception as e:
        logger.critical(
            f"---- Unhandled exception in __main__: {e} ----", exc_info=True
        )
    finally:
        logger.debug(
            "Main __main__ finally block: Checking OBD and raw socket for closure."
        )
        if (
            obd_connection
            and hasattr(obd_connection, "is_connected")
            and obd_connection.is_connected()
        ):
            logger.info("Closing python-obd connection.")
            try:
                obd_connection.close()  # This should close the stream it was given (our raw_obd_socket)
                logger.info("python-obd connection closed.")
            except Exception as e_obd_close:
                logger.error(
                    f"Exception while closing python-obd connection: {e_obd_close}",
                    exc_info=True,
                )

        logger.info("---- Python HUD Backend Application Shut Down ----")
