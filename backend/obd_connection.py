"""
OBD connection management module.
Handles initialization and maintenance of the OBD connection.
"""
import time
import obd
from logger_setup import logger
from config import OBD_TIMEOUT

# Global OBD Connection Object
obd_connection = None

def initialize_obd_connection(host: str, port: int, max_retries: int = 3, retry_delay: float = 2.0) -> bool:
    """
    Initialize connection to the OBD interface with retry mechanism.

    Args:
        host: The host name or IP address of the OBD interface.
        port: The port number of the OBD interface.
        max_retries: Maximum number of connection attempts.
        retry_delay: Delay between retries in seconds.

    Returns:
        True if connection was successful, False otherwise.
    """
    global obd_connection
    logger.debug(f"ENTER: initialize_obd_connection(host='{host}', port={port})")

    # Standard connection string format for python-OBD/pyserial TCP connections
    connection_string = f"socket://{host}:{port}"

    for attempt in range(1, max_retries + 1):
        logger.info(f"Attempt {attempt}/{max_retries} to connect to ELM327 at {connection_string}")
        try:
            obd_connection = obd.OBD(
                connection_string,
                baudrate=38400,        # Fixed baudrate for the emulator
                protocol=None,         # Let OBD-II auto-detect the protocol
                fast=False,            # Careful mode
                timeout=OBD_TIMEOUT,   # Use standard timeout
                check_voltage=False    # Skip voltage check for emulators
            )
            logger.debug("obd.OBD() instance created.")

            if obd_connection.is_connected():
                logger.info("python-OBD reports successful connection.")
                logger.info(f"Adapter status: {obd_connection.status()}")

                if obd_connection.protocol_id():
                    logger.info(
                        f"Protocol auto-detected: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})"
                    )
                    return True
                else:
                    logger.warning("No protocol auto-detected. Attempting to manually set to '6' (CAN 11-bit 500k).")
                    # Ensure we're still connected before trying to set protocol
                    if not obd_connection.is_connected(): # Check again, connection might have dropped
                        logger.error("Lost connection before attempting to manually set protocol.")
                        # Allow loop to handle close and retry
                    elif obd_connection.set_protocol("6"):
                        time.sleep(0.5)  # Give the adapter a moment to switch
                        if obd_connection.protocol_id() and obd_connection.protocol_name(): # Verify
                            logger.info(
                                f"Protocol manually set successfully: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})"
                            )
                            return True
                        else:
                            logger.error("Failed to confirm protocol after manual set command.")
                    else:
                        logger.error("Command to set_protocol('6') failed to send or was rejected by adapter.")
            else:
                logger.warning(f"python-obd failed to report a successful connection on attempt {attempt}.")

        except Exception as e:
            logger.error(
                f"Exception during OBD connection attempt {attempt} to {connection_string}: {e}",
                exc_info=True
            )
        finally:
            # If not successful by this point in the attempt, close and clean up
            if not (obd_connection and obd_connection.is_connected() and obd_connection.protocol_id()):
                if obd_connection:
                    try:
                        obd_connection.close()
                    except Exception as close_ex:
                        logger.warning(f"Exception during cleanup close on attempt {attempt}: {close_ex}")
                    obd_connection = None
        
        if attempt < max_retries:
            logger.info(f"Waiting {retry_delay} seconds before next attempt...")
            time.sleep(retry_delay)

    logger.error(f"Failed to connect to ELM327 at {connection_string} after {max_retries} attempts.")
    return False

def get_connection():
    """Get the current OBD connection object"""
    return obd_connection

def close_connection() -> bool:
    """
    Close the OBD connection if it exists and is connected.
    Sets the global obd_connection to None.
    Returns:
        True if the connection was closed successfully or was not active.
        False if an error occurred during closing an active connection.
    """
    global obd_connection
    if obd_connection:
        try:
            if obd_connection.is_connected():
                logger.info("Closing active python-obd connection.")
                obd_connection.close()
                logger.info("python-obd connection closed.")
            else:
                logger.info("OBD connection object existed but was not connected.")
        except Exception as e:
            logger.error(f"Exception while closing python-obd connection: {e}", exc_info=True)
            obd_connection = None # Ensure it's None even if close fails
            return False # Indicate error during close
        finally:
            obd_connection = None # Ensure it's always set to None after handling
    else:
        logger.debug("No OBD connection object to close.")
    return True