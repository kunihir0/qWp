#!/usr/bin/env python3
"""
OBD Sanity Check Script

This script performs a comprehensive check of the OBD connection:
1. Connects to the ELM327 adapter
2. Dumps all available data from the ECU
3. Displays a summary of supported commands
4. Waits for user confirmation before starting the WebSocket server
"""

import asyncio
import obd
import time
import sys
from logger_setup import logger
from config import OBD_EMULATOR_HOST, OBD_EMULATOR_PORT, OBD_TIMEOUT
from obd_connection import initialize_obd_connection, close_connection, get_connection
from websocket_server import start_server
from config import WS_HOST, WS_PORT

# List of important OBD commands to check
ESSENTIAL_COMMANDS = [
    "RPM", "SPEED", "COOLANT_TEMP", "THROTTLE_POS", 
    "ENGINE_LOAD", "FUEL_LEVEL", "INTAKE_TEMP", "MAF"
]

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def print_section(text):
    """Print a section header"""
    print("\n" + "-" * 80)
    print(f" {text} ".center(80, "-"))
    print("-" * 80)

async def sanity_check():
    """Perform a complete sanity check on the OBD connection"""
    print_header("OBD CONNECTION SANITY CHECK")
    print("\nConnecting to ELM327 adapter...")
    
    # Step 1: Initialize the connection
    connection_success = initialize_obd_connection(
        OBD_EMULATOR_HOST,
        OBD_EMULATOR_PORT,
        max_retries=3,
        retry_delay=2.0
    )
    
    if not connection_success:
        print("\n❌ ERROR: Failed to connect to the ELM327 adapter!")
        print(f"     Check that the emulator is running at {OBD_EMULATOR_HOST}:{OBD_EMULATOR_PORT}")
        print("     Make sure you've started the simulator with: elm -s car")
        return False
    
    # Get the OBD connection
    connection = get_connection()
    
    print("\n✅ Successfully connected to the ELM327 adapter!")
    print(f"   - Protocol: {connection.protocol_name()} (ID: {connection.protocol_id()})")
    print(f"   - Status: {connection.status()}")
    
    # Step 2: Check supported commands and protocols
    print_section("SUPPORTED PROTOCOLS AND COMMANDS")
    
    if connection.protocol_id():
        print(f"Active Protocol: {connection.protocol_name()} (ID: {connection.protocol_id()})")
    else:
        print("❌ No active protocol detected!")
    
    supported_count = len(connection.supported_commands)
    print(f"\nNumber of supported commands: {supported_count}")
    
    # Count and check essential commands
    essential_supported = []
    essential_missing = []
    
    for cmd_name in ESSENTIAL_COMMANDS:
        if hasattr(obd.commands, cmd_name):
            cmd = getattr(obd.commands, cmd_name)
            if cmd in connection.supported_commands:
                essential_supported.append(cmd_name)
            else:
                essential_missing.append(cmd_name)
        else:
            print(f"Warning: Command '{cmd_name}' not found in obd.commands library.")
    
    print(f"\nEssential commands supported: {len(essential_supported)}/{len(ESSENTIAL_COMMANDS)}")
    if essential_supported:
        print(f"   ✅ Supported: {', '.join(essential_supported)}")
    if essential_missing:
        print(f"   ❌ Missing: {', '.join(essential_missing)}")
    
    # Step 3: Query and display real-time data
    print_section("REAL-TIME OBD DATA")
    
    data = {}
    for cmd_name in ESSENTIAL_COMMANDS:
        if hasattr(obd.commands, cmd_name):
            cmd = getattr(obd.commands, cmd_name)
            response = connection.query(cmd)
            
            if not response.is_null():
                data[cmd_name] = {
                    "value": response.value,
                    "unit": response.unit
                }
                print(f"{cmd_name}: {response.value} {response.unit}")
            else:
                print(f"{cmd_name}: NULL RESPONSE")
        
    # Step 4: Wait for user confirmation
    print_section("CONFIRMATION")
    
    if len(essential_supported) == 0:
        print("❌ WARNING: No essential commands are supported by the ECU!")
        print("   The frontend will likely not display any meaningful data.")
    elif len(essential_supported) < len(ESSENTIAL_COMMANDS) / 2:
        print("⚠️ WARNING: Less than half of essential commands are supported!")
        print("   The frontend will have limited data to display.")
    else:
        print("✅ OBD connection is working properly!")
        print("   The frontend should be able to display meaningful data.")
    
    print("\nPress Enter to start the WebSocket server or Ctrl+C to exit...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nExiting without starting WebSocket server.")
        close_connection()
        return False
    
    # Step 5: Start WebSocket server
    print_section("STARTING WEBSOCKET SERVER")
    print(f"Starting WebSocket server at ws://{WS_HOST}:{WS_PORT}...")
    
    try:
        await start_server(WS_HOST, WS_PORT)
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to start WebSocket server: {e}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(sanity_check())
    except KeyboardInterrupt:
        print("\n\nSanity check interrupted. Exiting...")
    except Exception as e:
        print(f"\n❌ ERROR: Unhandled exception: {e}")
    finally:
        close_connection()
        print("\nOBD connection closed.")