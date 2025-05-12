"""
Configuration settings for the HUD Backend application.
Contains all configurable parameters and constants.
"""

# WebSocket Server Configuration
WS_HOST = "localhost"
WS_PORT = 8765

# OBD Connection Configuration
OBD_EMULATOR_HOST = "localhost"
OBD_EMULATOR_PORT = 35000
OBD_BAUDRATE = 38400
OBD_TIMEOUT = 3.0

# OBD Data Polling Configuration
OBD_POLLING_INTERVAL = 0.5  # Seconds between OBD queries