"""
OBD connection management module.
Handles initialization and maintenance of the OBD connection.
"""
import time
import obd
from logger_setup import logger
from config import OBD_BAUDRATE, OBD_TIMEOUT

# Global OBD Connection Object
obd_connection = None

def initialize_obd_connection(host, port):
    """
    Initialize connection to the OBD interface
    
    Args:
        host: The host name or IP address of the OBD interface
        port: The port number of the OBD interface
        
    Returns:
        True if connection was successful, False otherwise
    """
    global obd_connection
    logger.debug(f"ENTER: initialize_obd_connection(host='{host}', port={port})")

    try:
        connection_string = f"socket://{host}:{port}"
        logger.info(f"Initializing python-obd with connection string: {connection_string}")
        obd_connection = obd.OBD(
            connection_string,
            baudrate=OBD_BAUDRATE,       # From config
            protocol=None,        
            fast=False,           
            check_voltage=False,  
            timeout=OBD_TIMEOUT   # From config
        )
        logger.debug(f"obd.OBD() instance created: {obd_connection}")

        if obd_connection.is_connected():
            logger.info("python-obd reports successful connection.")
            status_result = obd_connection.status() 
            logger.info(f"Adapter status from python-obd: {status_result}")

            if obd_connection.protocol_id():
                logger.info(
                    f"Protocol successfully set/detected: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})"
                )
                return True
            else:
                logger.warning("No protocol auto-detected. Attempting to manually set to '6' (CAN).")
                if obd_connection.set_protocol("6"):
                    time.sleep(0.5)
                    if obd_connection.protocol_id():
                        logger.info(
                            f"Protocol manually set to: {obd_connection.protocol_name()} (ID: {obd_connection.protocol_id()})"
                        )
                        return True
                    else:
                        logger.error("Failed to manually set protocol after attempting. OBD queries may fail.")
                        obd_connection.close()
                        obd_connection = None
                        return False
                else:
                    logger.error("Command to set_protocol failed. OBD queries may fail.")
                    obd_connection.close()
                    obd_connection = None
                    return False
        else:
            logger.error(f"python-obd failed to report a successful connection using '{connection_string}'.")
            obd_connection = None
            return False

    except Exception as e:
        logger.error(
            f"General exception during OBD connection setup with '{connection_string}': {e}",
            exc_info=True,
        )
        obd_connection = None
        return False
    finally:
        logger.debug("EXIT: initialize_obd_connection")

def get_connection():
    """Get the current OBD connection object"""
    return obd_connection

def close_connection():
    """Close the OBD connection if it exists"""
    global obd_connection
    if obd_connection and hasattr(obd_connection, 'is_connected') and obd_connection.is_connected():
        logger.info("Closing python-obd connection.")
        try:
            obd_connection.close() 
            logger.info("python-obd connection closed.")
            obd_connection = None
            return True
        except Exception as e:
            logger.error(f"Exception while closing python-obd connection: {e}", exc_info=True)
            return False
    return True