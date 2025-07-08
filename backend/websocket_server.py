"""
WebSocket server module.
Handles WebSocket connections and streaming data to clients.
"""
import asyncio
import json
import websockets
import importlib.util

# Check if this module is being run directly
if __name__ == "__main__":
    # Use local imports when run as a script
    from logger_setup import logger
    from config import OBD_POLLING_INTERVAL, WS_HOST, WS_PORT
    from obd_data import query_obd_data
    from obd_connection import initialize_obd_connection, close_connection
    from config import OBD_EMULATOR_HOST, OBD_EMULATOR_PORT
else:
    # Use regular imports when imported as a module
    from logger_setup import logger
    from config import OBD_POLLING_INTERVAL
    from obd_data import query_obd_data

async def stream_obd_data_to_client(websocket):
    """
    Stream OBD data to a connected WebSocket client
    
    Args:
        websocket: The WebSocket connection
    """
    client_addr = websocket.remote_address
    logger.info(f"ENTER: stream_obd_data_to_client for {client_addr}")
    
    try:
        while True:
            logger.debug(f"OBD: stream_obd_data_to_client loop for {client_addr}. Querying OBD.")
            
            # Query OBD data
            data_to_send = await query_obd_data(client_addr)
            
            # Check for disconnected or no protocol states
            if data_to_send["status"] in ["OBD_DISCONNECTED", "OBD_NO_PROTOCOL"]:
                try:
                    await websocket.send(json.dumps(data_to_send))
                except websockets.exceptions.ConnectionClosed:
                    break
                # Wait longer between updates for error states
                await asyncio.sleep(2)
                continue
                
            # Count non-null values in the data_to_send
            non_null_values = sum(1 for key, value in data_to_send.items()
                              if value is not None and not key.endswith('_unit') and key != 'status' and key != 'dtcs')
            
            # Send the collected data
            json_payload_final = json.dumps(data_to_send)
            logger.debug(f"Sending final data packet to {client_addr} with {non_null_values} non-null values")
            logger.debug(f"Sample values - RPM: {data_to_send.get('rpm')}, Speed: {data_to_send.get('speed')}, Coolant: {data_to_send.get('coolant_temp')}")
            try:
                await websocket.send(json_payload_final)
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Client {client_addr} disconnected during final data send. Breaking stream loop.")
                break
            
            logger.debug(f"Sleeping for {OBD_POLLING_INTERVAL}s before next OBD query for {client_addr}")
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
        logger.error(f"Unhandled error in stream_obd_data_to_client for {client_addr}: {e}", exc_info=True)
        try:
            if hasattr(websocket, 'open') and websocket.open: 
                await websocket.send(json.dumps({"error": "Backend streaming error", "details": str(e)}))
        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"Client {client_addr} disconnected while trying to send final streaming error.")
        except Exception as e_send:
            logger.error(f"Further error sending final streaming error to {client_addr}: {e_send}")
    finally:
        logger.info(f"EXIT: stream_obd_data_to_client for {client_addr}")

async def handler(websocket):
    """
    Handle a WebSocket connection
    
    Args:
        websocket: The WebSocket connection
    """
    client_addr = websocket.remote_address
    logger.info(f"ENTER: handler for new client {client_addr}")
    streaming_task = None 
    try:
        logger.debug(f"Creating stream_obd_data_to_client task for {client_addr}")
        streaming_task = asyncio.create_task(stream_obd_data_to_client(websocket))
        async for message in websocket:
            logger.info(f"Received control message from {client_addr}: '{message}' (currently ignored by streaming logic)")
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"Connection with {client_addr} closed cleanly by client in main handler.")
    except websockets.exceptions.ConnectionClosedError as e:
        logger.warning(f"Connection with {client_addr} closed with error in main handler: {e}")
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
                logger.info(f"Streaming task for {client_addr} was successfully cancelled.")
            except Exception as e_task_cancel:
                logger.error(f"Exception while awaiting cancelled streaming task for {client_addr}: {e_task_cancel}", exc_info=True)
        elif streaming_task and streaming_task.done():
            logger.debug(f"Streaming task for {client_addr} was already done.")
        else:
            logger.debug(f"No streaming task to cancel or already cancelled for {client_addr}.")
        logger.info(f"EXIT: handler for client {client_addr}")

async def start_server(host, port):
    """
    Start the WebSocket server
    
    Args:
        host: The host address to bind to
        port: The port to listen on
    """
    logger.info(f"Attempting to start WebSocket server on ws://{host}:{port}")
    async with websockets.serve(handler, host, port):
        logger.info(f"WebSocket server started successfully at ws://{host}:{port}")
        logger.info("Waiting for frontend connections...")
        await asyncio.Future()  # Run forever

# Add main entry point for direct execution
if __name__ == "__main__":
    logger.info("---- Starting Python HUD Backend WebSocket Server (Standalone Mode) ----")
    try:
        # Initialize OBD when running as standalone
        initialize_obd_connection(OBD_EMULATOR_HOST, OBD_EMULATOR_PORT)
        
        # Start server
        asyncio.run(start_server(WS_HOST, WS_PORT))
    except KeyboardInterrupt:
        logger.info("\n---- WebSocket Server stopping due to KeyboardInterrupt ----")
    except Exception as e:
        logger.critical(f"---- Unhandled exception in standalone server: {e} ----", exc_info=True)
    finally:
        # Clean up resources
        close_connection()
        logger.info("---- WebSocket Server Shut Down ----")