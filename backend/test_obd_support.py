#!/usr/bin/env python3
"""
Script to test the OBD emulator connection and supported commands.
This will help diagnose which OBD commands are returning null responses.
"""
import asyncio
import obd
import json
from logger_setup import logger
from config import OBD_EMULATOR_HOST, OBD_EMULATOR_PORT, OBD_TIMEOUT

async def test_obd_commands():
    """
    Test all available OBD commands against the emulator
    and log which ones are supported.
    """
    # First create a connection to the emulator
    logger.info(f"Connecting to OBD emulator at {OBD_EMULATOR_HOST}:{OBD_EMULATOR_PORT}")
    
    connection_string = f"socket://{OBD_EMULATOR_HOST}:{OBD_EMULATOR_PORT}"
    
    try:
        # Connect to the emulator
        connection = obd.OBD(
            connection_string,
            baudrate=38400,
            protocol=None,
            fast=False,
            timeout=OBD_TIMEOUT,
            check_voltage=False
        )
        
        # Check if connected
        if not connection.is_connected():
            logger.error("Failed to connect to OBD emulator")
            return
            
        logger.info(f"Successfully connected to OBD emulator")
        logger.info(f"Protocol: {connection.protocol_name()} (ID: {connection.protocol_id()})")
        
        # Dictionary to store results
        results = {
            "supported_commands": [],
            "unsupported_commands": []
        }
        
        # List of common OBD commands to test
        commands_to_test = [
            "RPM", "SPEED", "COOLANT_TEMP", "THROTTLE_POS", "FUEL_LEVEL", "ENGINE_LOAD",
            "INTAKE_TEMP", "MAF", "FUEL_PRESSURE", "FUEL_RAIL_PRESSURE_ABS",
            "FUEL_TYPE", "STATUS", "VIN", "FUEL_STATUS", "O2_S1_WR_VOLTAGE",
            "OIL_TEMP", "DISTANCE_W_MIL", "CONTROL_MODULE_VOLTAGE"
        ]
        
        # Test each command
        for cmd_name in commands_to_test:
            if hasattr(obd.commands, cmd_name):
                cmd = getattr(obd.commands, cmd_name)
                logger.info(f"Testing command: {cmd_name}")
                
                # Query the command
                response = connection.query(cmd)
                
                # Log the result
                if response.is_null():
                    logger.info(f"Command {cmd_name} returned NULL response")
                    results["unsupported_commands"].append({
                        "name": cmd_name,
                        "desc": cmd.desc
                    })
                else:
                    logger.info(f"Command {cmd_name} SUPPORTED: {response.value} {response.unit}")
                    results["supported_commands"].append({
                        "name": cmd_name,
                        "desc": cmd.desc,
                        "value": str(response.value),
                        "unit": str(response.unit) if response.unit else None
                    })
            else:
                logger.warning(f"Command {cmd_name} not found in obd.commands")
                
        # Display summary
        logger.info(f"=== SUMMARY ===")
        logger.info(f"Supported commands: {len(results['supported_commands'])}")
        for cmd in results["supported_commands"]:
            logger.info(f"  - {cmd['name']}: {cmd['value']} {cmd['unit'] if cmd['unit'] else ''}")
            
        logger.info(f"Unsupported commands: {len(results['unsupported_commands'])}")
        for cmd in results["unsupported_commands"]:
            logger.info(f"  - {cmd['name']}")
            
        # Save results to file
        with open("obd_support_results.json", "w") as f:
            json.dump(results, f, indent=2)
            logger.info(f"Results saved to obd_support_results.json")
            
    except Exception as e:
        logger.error(f"Error testing OBD commands: {e}", exc_info=True)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("OBD connection closed")

if __name__ == "__main__":
    logger.info("=== OBD Support Test Script ===")
    asyncio.run(test_obd_commands())
    logger.info("=== Test Complete ===")