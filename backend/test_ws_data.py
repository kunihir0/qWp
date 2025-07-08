#!/usr/bin/env python3
"""
Script to test the WebSocket data stream from backend to frontend.
This will help diagnose what data is actually being sent to the frontend.
"""
import asyncio
import websockets
import json
from logger_setup import logger
from config import OBD_EMULATOR_HOST, OBD_EMULATOR_PORT, OBD_TIMEOUT
from obd_connection import initialize_obd_connection
from obd_data import query_obd_data

async def test_websocket_data():
    """
    Test the WebSocket data stream by simulating what the backend would send to the frontend
    """
    # First, initialize the OBD connection
    logger.info(f"Initializing OBD connection to {OBD_EMULATOR_HOST}:{OBD_EMULATOR_PORT}")
    connection_success = initialize_obd_connection(
        OBD_EMULATOR_HOST,
        OBD_EMULATOR_PORT,
        max_retries=2,
        retry_delay=1.0
    )
    
    if not connection_success:
        logger.error("Failed to connect to OBD emulator. Test cannot proceed.")
        return
        
    logger.info("OBD connection successful")
    
    # Query OBD data (simulates what the websocket server would do)
    logger.info("Querying OBD data...")
    data = await query_obd_data()
    
    # Log some basic stats about the data
    non_null_values = sum(1 for key, value in data.items() 
                       if value is not None and not key.endswith('_unit') and key != 'status' and key != 'dtcs')
    
    null_values = sum(1 for key, value in data.items() 
                    if value is None and not key.endswith('_unit') and key != 'dtcs')
    
    total_fields = non_null_values + null_values
    
    logger.info(f"Data stats: {non_null_values}/{total_fields} non-null values ({(non_null_values/total_fields)*100:.1f}%)")
    
    # Check specific important fields
    critical_fields = ['rpm', 'speed', 'coolant_temp', 'throttle_pos', 'fuel_level', 'engine_load']
    logger.info("Critical field values:")
    for field in critical_fields:
        logger.info(f"  - {field}: {data.get(field, 'MISSING')} {data.get(f'{field}_unit', '')}")
    
    # Check if all expected fields are present (not just null but actually in the data)
    logger.info("All expected fields present in data? " + 
               str(all(field in data for field in critical_fields)))
    
    # Save full JSON to file for inspection
    with open("websocket_data_sample.json", "w") as f:
        json.dump(data, f, indent=2)
        logger.info(f"Full data saved to websocket_data_sample.json")

if __name__ == "__main__":
    logger.info("=== WebSocket Data Test Script ===")
    asyncio.run(test_websocket_data())
    logger.info("=== Test Complete ===")