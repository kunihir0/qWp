"""
HUD Backend Application - Main Module
Orchestrates the HUD Backend application by initializing components and starting services.
"""
import asyncio
from logger_setup import logger
from config import WS_HOST, WS_PORT, OBD_EMULATOR_HOST, OBD_EMULATOR_PORT
from obd_connection import initialize_obd_connection, close_connection
from websocket_server import start_server

async def main_async_runner():
    """
    Main async runner function.
    Initializes components and starts the WebSocket server.
    """
    logger.debug("ENTER: main_async_runner")
    
    # Initialize OBD connection
    initialize_obd_connection(OBD_EMULATOR_HOST, OBD_EMULATOR_PORT)
    
    # Start WebSocket server
    await start_server(WS_HOST, WS_PORT)
    
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
        # Clean up resources
        close_connection()
        logger.info("---- Python HUD Backend Application Shut Down ----")
