"""
Logger configuration module for the HUD Backend application.
Sets up logging for the main application, OBD library, and WebSockets.
"""
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            "level": record.levelname,
            "name": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_loggers():
    """Configure all loggers for the application with JSON formatting"""
    json_formatter = JsonFormatter()

    # Configure root logger
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    # Remove existing handlers to avoid duplicate logs or format conflicts
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # Add new handler with JSON formatter
    stream_handler_root = logging.StreamHandler()
    stream_handler_root.setFormatter(json_formatter)
    root_logger.addHandler(stream_handler_root)

    # Configure main application logger
    logger = logging.getLogger("HUD_Backend")
    logger.setLevel(logging.DEBUG)
    # Ensure it uses the root logger's handlers or configure its own
    logger.propagate = True # Let root logger handle it, or set to False and add handler below

    # Configure OBD logger
    obd_logger = logging.getLogger("obd")
    obd_logger.setLevel(logging.DEBUG)
    if not obd_logger.handlers:
        stream_handler_obd = logging.StreamHandler()
        stream_handler_obd.setFormatter(json_formatter)
        obd_logger.addHandler(stream_handler_obd)
    obd_logger.propagate = False
    
    # Configure WebSockets logger
    ws_logger = logging.getLogger("websockets")
    ws_logger.setLevel(logging.DEBUG)
    if not ws_logger.handlers:
        ws_stream_handler = logging.StreamHandler()
        ws_stream_handler.setFormatter(json_formatter)
        ws_logger.addHandler(ws_stream_handler)
    ws_logger.propagate = False
        
    logger.info("JSON logging configured.")
    
    return logger

# Export main logger for use in other modules
logger = setup_loggers()