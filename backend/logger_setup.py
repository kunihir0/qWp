"""
Logger configuration module for the HUD Backend application.
Sets up logging for the main application, OBD library, and WebSockets.
"""
import logging

def setup_loggers():
    """Configure all loggers for the application"""
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configure main application logger
    logger = logging.getLogger("HUD_Backend")
    logger.setLevel(logging.DEBUG)
    
    # Configure OBD logger
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
    
    # Configure WebSockets logger
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
    
    return logger

# Export main logger for use in other modules
logger = setup_loggers()