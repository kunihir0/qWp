"""
OBD data handling module.
Contains functions for querying and processing OBD data.
"""
import asyncio
import obd
import re
from logger_setup import logger
from obd_connection import get_connection

# Dictionary of World Manufacturer Identifiers (first 3 characters of VIN)
MANUFACTURER_CODES = {
    # North American Manufacturers
    "1G": "General Motors (US)",
    "1G1": "Chevrolet",
    "1GC": "Chevrolet Truck",
    "1GD": "GMC Truck",
    "1GM": "Pontiac",
    "1G2": "Pontiac",
    "1G3": "Oldsmobile",
    "1G4": "Buick",
    "1G6": "Cadillac",
    "1H": "Honda (US)",
    "1HD": "Harley-Davidson",
    "1J": "Jeep",
    "1L": "Lincoln",
    "1M": "Mercury",
    "1N": "Nissan (US)",
    "1V": "Volkswagen (US)",
    "1Y": "General Motors (US)",
    "2F": "Ford (Canada)",
    "2G": "General Motors (Canada)",
    "2H": "Honda (Canada)",
    "2M": "Mercury (Canada)",
    "2T": "Toyota (Canada)",
    "3F": "Ford (Mexico)",
    "3G": "General Motors (Mexico)",
    "3H": "Honda (Mexico)",
    "3N": "Nissan (Mexico)",
    "3V": "Volkswagen (Mexico)",
    "4F": "Mazda (USA)",
    "4M": "Mercury (Mexico)",
    "4S": "Subaru (USA)",
    "4T": "Toyota (USA)",
    "4U": "Subaru",
    "5F": "Honda (US)",
    "5L": "Lincoln (US)",
    "5N": "Hyundai (Korea)",
    "5T": "Toyota (US Truck)",
    "5Y": "Mazda (US)",
    "JA": "Isuzu",
    "JF": "Fuji Heavy Industries (Subaru)",
    "JH": "Honda (Japan)",
    "JM": "Mazda (Japan)",
    "JN": "Nissan (Japan)",
    "JS": "Suzuki (Japan)",
    "JT": "Toyota (Japan)",
    "KL": "Daewoo/GM Korea",
    "KM": "Hyundai",
    "KN": "Kia",
    "L5": "Lincoln",
    "NM": "Mitsubishi (Japan)",
    "SAL": "Land Rover",
    "SAJ": "Jaguar",
    "SAR": "Rover",
    "SCC": "Lotus",
    "SCF": "Aston Martin",
    "SDB": "Peugeot",
    "SFD": "Alexander Dennis",
    "SHS": "Honda (UK)",
    "SJN": "Nissan (UK)",
    "TM": "Mitsubishi (Japan)",
    "TMB": "Skoda",
    "TRU": "Audi",
    "VF1": "Renault",
    "VF3": "Peugeot",
    "VF7": "Citroën",
    "VNK": "Toyota (Japan)",
    "VS5": "Toyota (Japan)",
    "VV": "Volkswagen (Spain)",
    "VWV": "Volkswagen",
    "W0L": "Opel/Vauxhall",
    "WA1": "Audi SUV",
    "WAU": "Audi",
    "WBA": "BMW",
    "WBS": "BMW M",
    "WDB": "Mercedes-Benz",
    "WDC": "Mercedes-Benz SUV",
    "WDD": "Mercedes-Benz",
    "WMW": "Mini",
    "WP0": "Porsche",
    "WP1": "Porsche SUV",
    "WUA": "Audi Sport",
    "WVG": "Volkswagen SUV",
    "WVW": "Volkswagen",
    "XL9": "Spyker",
    "XTA": "Lada/AvtoVAZ",
    "YK1": "Saab",
    "YS3": "Saab",
    "YV1": "Volvo",
    "YV4": "Volvo SUV",
    "ZA9": "Bugatti",
    "ZAR": "Alfa Romeo",
    "ZFA": "Fiat",
    "ZFF": "Ferrari"
}

def decode_vin(vin):
    """
    Decode a VIN to extract vehicle information
    
    Args:
        vin: The Vehicle Identification Number
        
    Returns:
        Dictionary containing vehicle information
    """
    if not vin or len(vin) != 17:
        return {
            "make": None,
            "model_year": None,
            "country": None,
            "raw_vin": vin
        }
    
    # Extract manufacturer/make
    wmi = vin[:3]
    make = None
    for code, manufacturer in MANUFACTURER_CODES.items():
        if vin.startswith(code):
            make = manufacturer
            break
    
    # If no exact match found, try first 2 characters
    if make is None and wmi[:2] in MANUFACTURER_CODES:
        make = MANUFACTURER_CODES[wmi[:2]]
    
    # Extract model year (10th character)
    year_char = vin[9]
    base_year = 1980
    model_year = None
    
    # Year coding
    year_map = {
        'A': 1980, 'B': 1981, 'C': 1982, 'D': 1983, 'E': 1984, 'F': 1985, 'G': 1986, 'H': 1987,
        'J': 1988, 'K': 1989, 'L': 1990, 'M': 1991, 'N': 1992, 'P': 1993, 'R': 1994, 'S': 1995,
        'T': 1996, 'V': 1997, 'W': 1998, 'X': 1999, 'Y': 2000, '1': 2001, '2': 2002, '3': 2003,
        '4': 2004, '5': 2005, '6': 2006, '7': 2007, '8': 2008, '9': 2009, 'A': 2010, 'B': 2011,
        'C': 2012, 'D': 2013, 'E': 2014, 'F': 2015, 'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019,
        'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024
    }
    
    if year_char in year_map:
        model_year = year_map[year_char]
    
    # Determine country of manufacture
    country = None
    first_char = vin[0]
    
    country_codes = {
        '1': 'United States',
        '2': 'Canada',
        '3': 'Mexico',
        '4': 'United States',
        '5': 'United States',
        'J': 'Japan',
        'K': 'Korea',
        'L': 'China',
        'S': 'United Kingdom',
        'T': 'Switzerland/Japan',
        'V': 'France/Spain',
        'W': 'Germany',
        'X': 'Russia/USSR',
        'Y': 'Belgium/Finland/Sweden',
        'Z': 'Italy'
    }
    
    if first_char in country_codes:
        country = country_codes[first_char]
    
    return {
        "make": make,
        "model_year": model_year,
        "country": country,
        "raw_vin": vin
    }

def _process_value(responses, command_name, data_dict, data_key):
    """
    Helper method to process OBD response values consistently
    
    Args:
        responses: Dictionary of responses from OBD queries
        command_name: Name of the command in the responses dictionary
        data_dict: Dictionary to store the processed value
        data_key: Key in data_dict where the value should be stored
    """
    if command_name in responses and not responses[command_name].is_null():
        # Get the value, handling pint quantities if present
        value = responses[command_name].value
        if hasattr(value, 'magnitude'):
            # Round numeric values to 2 decimal places for cleaner display
            data_dict[data_key] = round(value.magnitude, 2)
        else:
            data_dict[data_key] = value
            
        # Store unit if available
        unit_key = f"{data_key}_unit"
        if unit_key in data_dict and responses[command_name].unit:
            data_dict[unit_key] = str(responses[command_name].unit)

async def query_obd_command(cmd, client_addr=None):
    """
    Query a single OBD command asynchronously
    
    Args:
        cmd: The OBD command to query
        client_addr: Optional client address for logging
        
    Returns:
        The response from the OBD query
    """
    obd_connection = get_connection()
    address_info = f" for {client_addr}" if client_addr else ""
    
    logger.debug(f"Querying {cmd.name}{address_info}...")
    response = await asyncio.to_thread(obd_connection.query, cmd)
    logger.debug(f"{cmd.name} response{address_info}: Raw={response}, Value={response.value}, Unit={response.unit}, IsNull={response.is_null()}")
    
    return response

async def query_obd_data(client_addr=None):
    """
    Query all relevant OBD data and format it for transmission
    
    Args:
        client_addr: Optional client address for logging
        
    Returns:
        Dictionary containing formatted OBD data
    """
    obd_connection = get_connection()
    
    data_to_send = {
        # Currently implemented
        "rpm": None, "rpm_unit": "rpm",
        "speed": None, "speed_unit": "mph",
        "coolant_temp": None, "coolant_temp_unit": "celsius",
        "throttle_pos": None, "throttle_pos_unit": "%",
        "fuel_level": None, "fuel_level_unit": "%",
        "engine_load": None, "engine_load_unit": "%",
        "mil_on": False,
        "dtc_count": 0,
        "dtcs": [],
        
        # Engine and Fuel System
        "intake_temp": None, "intake_temp_unit": "celsius",
        "maf": None, "maf_unit": "grams/sec",
        "fuel_pressure": None, "fuel_pressure_unit": "kPa",
        "fuel_rail_pressure": None, "fuel_rail_pressure_unit": "kPa",
        "fuel_rail_pressure_direct": None, "fuel_rail_pressure_direct_unit": "kPa",
        "fuel_injection_timing": None, "fuel_injection_timing_unit": "degrees",
        "fuel_rate": None, "fuel_rate_unit": "L/h",
        "short_fuel_trim_1": None, "short_fuel_trim_1_unit": "%",
        "long_fuel_trim_1": None, "long_fuel_trim_1_unit": "%",
        "short_fuel_trim_2": None, "short_fuel_trim_2_unit": "%",
        "long_fuel_trim_2": None, "long_fuel_trim_2_unit": "%",
        "fuel_type": None,
        "ethanol_percent": None, "ethanol_percent_unit": "%",
        "evap_vapor_pressure": None, "evap_vapor_pressure_unit": "Pa",
        
        # Emissions System
        "o2_sensor_1_voltage": None, "o2_sensor_1_voltage_unit": "V",
        "o2_sensor_2_voltage": None, "o2_sensor_2_voltage_unit": "V",
        "catalyst_temp_b1s1": None, "catalyst_temp_b1s1_unit": "celsius",
        "catalyst_temp_b2s1": None, "catalyst_temp_b2s1_unit": "celsius",
        "egr_error": None, "egr_error_unit": "%",
        "egr_commanded": None, "egr_commanded_unit": "%",
        "evap_vapor_pressure_abs": None, "evap_vapor_pressure_abs_unit": "kPa",
        
        # Additional Temperatures
        "ambient_air_temp": None, "ambient_air_temp_unit": "celsius",
        "engine_oil_temp": None, "engine_oil_temp_unit": "celsius",
        "fuel_temp": None, "fuel_temp_unit": "celsius",
        
        # Vehicle/Driving Dynamics
        "timing_advance": None, "timing_advance_unit": "degrees",
        "abs_throttle_pos": None, "abs_throttle_pos_unit": "%",
        "rel_throttle_pos": None, "rel_throttle_pos_unit": "%",
        "accel_pedal_pos": None, "accel_pedal_pos_unit": "%",
        "commanded_throttle": None, "commanded_throttle_unit": "%",
        "manifold_pressure": None, "manifold_pressure_unit": "kPa",
        "baro_pressure": None, "baro_pressure_unit": "kPa",
        "abs_load": None, "abs_load_unit": "%",
        "rel_load": None, "rel_load_unit": "%",
        "distance_with_mil": None, "distance_with_mil_unit": "km",
        "distance_since_codes_cleared": None, "distance_since_codes_cleared_unit": "km",
        "runtime_since_engine_start": None, "runtime_since_engine_start_unit": "seconds",
        "time_since_codes_cleared": None, "time_since_codes_cleared_unit": "minutes",
        
        # Battery/Electrical
        "control_module_voltage": None, "control_module_voltage_unit": "V",
        "hybrid_battery_remaining": None, "hybrid_battery_remaining_unit": "%",
        
        # Advanced Engine Data
        "engine_friction_percent": None, "engine_friction_percent_unit": "%",
        "driver_demand_torque": None, "driver_demand_torque_unit": "%",
        "actual_engine_torque": None, "actual_engine_torque_unit": "%",
        "engine_ref_torque": None, "engine_ref_torque_unit": "Nm",
        "boost_pressure": None, "boost_pressure_unit": "kPa",
        "charge_air_temp": None, "charge_air_temp_unit": "celsius",
        
        # Vehicle Information
        "vin": None,
        "ecu_name": None,
        "fuel_system_status": None,
        "obd_standards": None,
        
        # Decoded Vehicle Information
        "vehicle_make": None,
        "vehicle_year": None,
        "vehicle_country": None,
        
        "status": "OK"
    }
    
    if not obd_connection or not obd_connection.is_connected():
        data_to_send["status"] = "OBD_DISCONNECTED"
        return data_to_send
        
    if not obd_connection.protocol_id():
        data_to_send["status"] = "OBD_NO_PROTOCOL"
        return data_to_send
    
    try:
        # Query Standard PIDs
        # Note: Not all vehicles support all PIDs - this is an extensive list
        commands_to_query = [
            # Currently implemented PIDs
            obd.commands.RPM,
            obd.commands.SPEED,
            obd.commands.COOLANT_TEMP,
            obd.commands.THROTTLE_POS,
            obd.commands.FUEL_LEVEL,
            obd.commands.ENGINE_LOAD,
            
            # Engine and Fuel System
            obd.commands.INTAKE_TEMP,
            obd.commands.MAF,
            obd.commands.FUEL_PRESSURE,
            obd.commands.FUEL_RAIL_PRESSURE,
            obd.commands.FUEL_RAIL_PRESSURE_DIRECT,
            obd.commands.FUEL_INJECT_TIMING,
            obd.commands.FUEL_RATE,
            obd.commands.SHORT_FUEL_TRIM_1,
            obd.commands.LONG_FUEL_TRIM_1,
            obd.commands.SHORT_FUEL_TRIM_2,
            obd.commands.LONG_FUEL_TRIM_2,
            obd.commands.FUEL_TYPE,
            obd.commands.ETHANOL_PERCENT,
            obd.commands.EVAP_VAPOR_PRESSURE,
            
            # Emissions System
            obd.commands.O2_S1_WR_VOLTAGE,
            obd.commands.O2_S2_WR_VOLTAGE,
            obd.commands.CATALYST_TEMP_B1S1,
            obd.commands.CATALYST_TEMP_B2S1,
            obd.commands.EGR_ERROR,
            obd.commands.COMMANDED_EGR,
            obd.commands.EVAP_VAPOR_PRESSURE_ABS,
            
            # Additional Temperatures
            obd.commands.AMBIENT_AIR_TEMP,
            obd.commands.OIL_TEMP,
            obd.commands.FUEL_TEMP,
            
            # Vehicle/Driving Dynamics
            obd.commands.TIMING_ADVANCE,
            obd.commands.ABSOLUTE_THROTTLE_POS,
            obd.commands.RELATIVE_THROTTLE_POS,
            obd.commands.ACCELERATOR_POS_D,
            obd.commands.COMMANDED_THROTTLE_ACTUATOR,
            obd.commands.INTAKE_PRESSURE,
            obd.commands.BAROMETRIC_PRESSURE,
            obd.commands.ABSOLUTE_LOAD,
            obd.commands.RELATIVE_LOAD,
            obd.commands.DISTANCE_W_MIL,
            obd.commands.DISTANCE_SINCE_DTC_CLEAR,
            obd.commands.RUN_TIME,
            obd.commands.TIME_SINCE_DTC_CLEARED,
            
            # Battery/Electrical
            obd.commands.CONTROL_MODULE_VOLTAGE,
            obd.commands.HYBRID_BATTERY_REMAINING,
            
            # Advanced Engine Data
            obd.commands.ENGINE_FRICTION_PERCENT,
            obd.commands.DRIVER_DEMAND_ENGINE_TORQUE,
            obd.commands.ACTUAL_ENGINE_TORQUE,
            obd.commands.ENGINE_REFERENCE_TORQUE,
            obd.commands.BOOST_PRESSURE_CONTROL,
            obd.commands.CHARGE_AIR_TEMP,
            
            # Vehicle Information
            obd.commands.VIN,
            obd.commands.ECU_NAME,
            obd.commands.FUEL_STATUS,
            obd.commands.OBD_COMPLIANCE
        ]
        
        responses = {}
        for cmd in commands_to_query:
            responses[cmd.name] = await query_obd_command(cmd, client_addr)

        # Process RPM
        if responses["RPM"] and not responses["RPM"].is_null():
            data_to_send["rpm"] = round(responses["RPM"].value.magnitude, 2) if hasattr(responses["RPM"].value, 'magnitude') else responses["RPM"].value
            data_to_send["rpm_unit"] = str(responses["RPM"].unit)

        # Process Speed (and convert to MPH)
        if responses["SPEED"] and not responses["SPEED"].is_null():
            speed_kmph = responses["SPEED"].value.magnitude if hasattr(responses["SPEED"].value, 'magnitude') else responses["SPEED"].value
            data_to_send["speed"] = round(speed_kmph * 0.621371, 2)
            # data_to_send["speed_unit"] is already "mph"

        # Process Coolant Temp
        if responses["COOLANT_TEMP"] and not responses["COOLANT_TEMP"].is_null():
            data_to_send["coolant_temp"] = responses["COOLANT_TEMP"].value.magnitude if hasattr(responses["COOLANT_TEMP"].value, 'magnitude') else responses["COOLANT_TEMP"].value
            data_to_send["coolant_temp_unit"] = str(responses["COOLANT_TEMP"].unit)
        
        # Process Throttle Position
        if responses["THROTTLE_POS"] and not responses["THROTTLE_POS"].is_null():
            data_to_send["throttle_pos"] = round(responses["THROTTLE_POS"].value.magnitude, 2) if hasattr(responses["THROTTLE_POS"].value, 'magnitude') else responses["THROTTLE_POS"].value
            data_to_send["throttle_pos_unit"] = str(responses["THROTTLE_POS"].unit)

        # Process Fuel Level
        if responses["FUEL_LEVEL"] and not responses["FUEL_LEVEL"].is_null():
            data_to_send["fuel_level"] = round(responses["FUEL_LEVEL"].value.magnitude, 2) if hasattr(responses["FUEL_LEVEL"].value, 'magnitude') else responses["FUEL_LEVEL"].value
            data_to_send["fuel_level_unit"] = str(responses["FUEL_LEVEL"].unit)

        # Process Engine Load
        if responses["ENGINE_LOAD"] and not responses["ENGINE_LOAD"].is_null():
            data_to_send["engine_load"] = round(responses["ENGINE_LOAD"].value.magnitude, 2) if hasattr(responses["ENGINE_LOAD"].value, 'magnitude') else responses["ENGINE_LOAD"].value
            data_to_send["engine_load_unit"] = str(responses["ENGINE_LOAD"].unit)
            
        # Process additional data - Engine and Fuel System
        _process_value(responses, "INTAKE_TEMP", data_to_send, "intake_temp")
        _process_value(responses, "MAF", data_to_send, "maf")
        _process_value(responses, "FUEL_PRESSURE", data_to_send, "fuel_pressure")
        _process_value(responses, "FUEL_RAIL_PRESSURE", data_to_send, "fuel_rail_pressure")
        _process_value(responses, "FUEL_RAIL_PRESSURE_DIRECT", data_to_send, "fuel_rail_pressure_direct")
        _process_value(responses, "FUEL_INJECT_TIMING", data_to_send, "fuel_injection_timing")
        _process_value(responses, "FUEL_RATE", data_to_send, "fuel_rate")
        _process_value(responses, "SHORT_FUEL_TRIM_1", data_to_send, "short_fuel_trim_1")
        _process_value(responses, "LONG_FUEL_TRIM_1", data_to_send, "long_fuel_trim_1")
        _process_value(responses, "SHORT_FUEL_TRIM_2", data_to_send, "short_fuel_trim_2")
        _process_value(responses, "LONG_FUEL_TRIM_2", data_to_send, "long_fuel_trim_2")
        
        # Special handling for string values
        if "FUEL_TYPE" in responses and not responses["FUEL_TYPE"].is_null():
            data_to_send["fuel_type"] = str(responses["FUEL_TYPE"].value)
        
        _process_value(responses, "ETHANOL_PERCENT", data_to_send, "ethanol_percent")
        _process_value(responses, "EVAP_VAPOR_PRESSURE", data_to_send, "evap_vapor_pressure")
        
        # Process Emissions System data
        _process_value(responses, "O2_S1_WR_VOLTAGE", data_to_send, "o2_sensor_1_voltage")
        _process_value(responses, "O2_S2_WR_VOLTAGE", data_to_send, "o2_sensor_2_voltage")
        _process_value(responses, "CATALYST_TEMP_B1S1", data_to_send, "catalyst_temp_b1s1")
        _process_value(responses, "CATALYST_TEMP_B2S1", data_to_send, "catalyst_temp_b2s1")
        _process_value(responses, "EGR_ERROR", data_to_send, "egr_error")
        _process_value(responses, "COMMANDED_EGR", data_to_send, "egr_commanded")
        _process_value(responses, "EVAP_VAPOR_PRESSURE_ABS", data_to_send, "evap_vapor_pressure_abs")
        
        # Process Additional Temperature data
        _process_value(responses, "AMBIENT_AIR_TEMP", data_to_send, "ambient_air_temp")
        _process_value(responses, "OIL_TEMP", data_to_send, "engine_oil_temp")
        _process_value(responses, "FUEL_TEMP", data_to_send, "fuel_temp")
        
        # Process Vehicle/Driving Dynamics data
        _process_value(responses, "TIMING_ADVANCE", data_to_send, "timing_advance")
        _process_value(responses, "ABSOLUTE_THROTTLE_POS", data_to_send, "abs_throttle_pos")
        _process_value(responses, "RELATIVE_THROTTLE_POS", data_to_send, "rel_throttle_pos")
        _process_value(responses, "ACCELERATOR_POS_D", data_to_send, "accel_pedal_pos")
        _process_value(responses, "COMMANDED_THROTTLE_ACTUATOR", data_to_send, "commanded_throttle")
        _process_value(responses, "INTAKE_PRESSURE", data_to_send, "manifold_pressure")
        _process_value(responses, "BAROMETRIC_PRESSURE", data_to_send, "baro_pressure")
        _process_value(responses, "ABSOLUTE_LOAD", data_to_send, "abs_load")
        _process_value(responses, "RELATIVE_LOAD", data_to_send, "rel_load")
        _process_value(responses, "DISTANCE_W_MIL", data_to_send, "distance_with_mil")
        _process_value(responses, "DISTANCE_SINCE_DTC_CLEAR", data_to_send, "distance_since_codes_cleared")
        _process_value(responses, "RUN_TIME", data_to_send, "runtime_since_engine_start")
        _process_value(responses, "TIME_SINCE_DTC_CLEARED", data_to_send, "time_since_codes_cleared")
        
        # Process Battery/Electrical data
        _process_value(responses, "CONTROL_MODULE_VOLTAGE", data_to_send, "control_module_voltage")
        _process_value(responses, "HYBRID_BATTERY_REMAINING", data_to_send, "hybrid_battery_remaining")
        
        # Process Advanced Engine data
        _process_value(responses, "ENGINE_FRICTION_PERCENT", data_to_send, "engine_friction_percent")
        _process_value(responses, "DRIVER_DEMAND_ENGINE_TORQUE", data_to_send, "driver_demand_torque")
        _process_value(responses, "ACTUAL_ENGINE_TORQUE", data_to_send, "actual_engine_torque")
        _process_value(responses, "ENGINE_REFERENCE_TORQUE", data_to_send, "engine_ref_torque")
        _process_value(responses, "BOOST_PRESSURE_CONTROL", data_to_send, "boost_pressure")
        _process_value(responses, "CHARGE_AIR_TEMP", data_to_send, "charge_air_temp")
        
        # Process Vehicle Information
        if "VIN" in responses and not responses["VIN"].is_null():
            vin_value = str(responses["VIN"].value)
            data_to_send["vin"] = vin_value
            
            # Decode VIN to extract additional information
            if vin_value and len(vin_value) == 17:  # Standard VIN length
                vehicle_info = decode_vin(vin_value)
                data_to_send["vehicle_make"] = vehicle_info["make"]
                data_to_send["vehicle_year"] = vehicle_info["model_year"]
                data_to_send["vehicle_country"] = vehicle_info["country"]
                logger.debug(f"Decoded VIN: {vin_value} -> Make: {vehicle_info['make']}, Year: {vehicle_info['model_year']}, Country: {vehicle_info['country']}")
        
        if "ECU_NAME" in responses and not responses["ECU_NAME"].is_null():
            data_to_send["ecu_name"] = str(responses["ECU_NAME"].value)
        
        if "FUEL_STATUS" in responses and not responses["FUEL_STATUS"].is_null():
            data_to_send["fuel_system_status"] = str(responses["FUEL_STATUS"].value)
        
        if "OBD_COMPLIANCE" in responses and not responses["OBD_COMPLIANCE"].is_null():
            data_to_send["obd_standards"] = str(responses["OBD_COMPLIANCE"].value)

        # Query DTCs and MIL Status
        status_response = await query_obd_command(obd.commands.STATUS, client_addr)
        if status_response and not status_response.is_null():
            # STATUS command value is a tuple: (MIL_ON, DTC_COUNT, IGNITION_TYPE)
            data_to_send["mil_on"] = status_response.value[0] if isinstance(status_response.value, tuple) and len(status_response.value) > 0 else False
            data_to_send["dtc_count"] = status_response.value[1] if isinstance(status_response.value, tuple) and len(status_response.value) > 1 else 0
        
        if data_to_send["mil_on"] and data_to_send["dtc_count"] > 0:
            logger.debug(f"MIL is ON, DTC count: {data_to_send['dtc_count']}. Querying DTCs for {client_addr}...")
            dtc_response = await query_obd_command(obd.commands.GET_DTC, client_addr)
            if dtc_response and not dtc_response.is_null():
                # GET_DTC value is a list of tuples: [(CODE, DESCRIPTION), ...]
                data_to_send["dtcs"] = [{"code": dtc[0], "desc": dtc[1]} for dtc in dtc_response.value]
        
        data_to_send["status"] = "OK"
        
    except Exception as e:
        logger.error(f"Error querying OBD or processing data for {client_addr}: {e}", exc_info=True)
        data_to_send["status"] = "OBD_QUERY_ERROR"
        data_to_send["error_details"] = str(e)
    
    return data_to_send