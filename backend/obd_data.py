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

def _process_individual_obd_response(response, original_cmd_name_str):
    """
    Process an individual OBD response, handling type conversions, units, and special cases.

    Args:
        response: The obd.OBDResponse object.
        original_cmd_name_str: The string name of the command (e.g., "RPM", "SPEED").

    Returns:
        A tuple (processed_value, unit_str).
        Returns (None, None) if the response is null or processing fails.
    """
    if response.is_null():
        logger.debug(f"Command {original_cmd_name_str} response is null.")
        return None, None

    val = response.value
    unit = str(response.unit) if response.unit else None

    # Handle pint quantities
    if hasattr(val, 'magnitude'):
        processed_val = round(val.magnitude, 2)
        # Use pint's unit if available, otherwise the response's unit
        unit = str(val.units) if hasattr(val, 'units') else unit
    else:
        processed_val = val

    # Special handling based on command name
    if original_cmd_name_str == "SPEED":
        if isinstance(processed_val, (int, float)):  # Assuming original is km/h
            processed_val = round(processed_val * 0.621371, 2)
            unit = "mph"
    elif original_cmd_name_str in ["FUEL_TYPE", "VIN", "ECU_NAME", "FUEL_STATUS", "OBD_COMPLIANCE"]:
        processed_val = str(val)  # Ensure string representation
        unit = None  # These typically don't have units in the same sense
    elif original_cmd_name_str == "STATUS":
        # Value is a tuple (MIL_ON, DTC_COUNT, IGNITION_TYPE)
        processed_val = val  # Return the tuple as is
        unit = None
    elif original_cmd_name_str == "GET_DTC":
        # Value is a list of tuples [(CODE, DESCRIPTION), ...]
        processed_val = val  # Return the list of tuples as is
        unit = None
    
    # Default rounding for other numeric float types if not already a pint quantity
    if isinstance(processed_val, float) and not hasattr(val, 'magnitude'):
        processed_val = round(processed_val, 2)

    return processed_val, unit

async def query_obd_command(cmd_obj, original_cmd_name_str, client_addr=None):
    """
    Query a single OBD command asynchronously and process its response.

    Args:
        cmd_obj: The OBD command object to query.
        original_cmd_name_str: The original string name of the command (for logging and mapping).
        client_addr: Optional client address for logging.

    Returns:
        A tuple: (original_cmd_name_str, processed_value, unit_str, is_error_flag)
        is_error_flag is True if query failed, response was null, or processing failed.
    """
    obd_connection = get_connection()
    address_info = f" for {client_addr}" if client_addr else ""
    
    try:
        logger.debug(f"Querying {original_cmd_name_str} (obj: {cmd_obj.name}){address_info}...")
        response = await asyncio.to_thread(obd_connection.query, cmd_obj)
        logger.debug(f"{original_cmd_name_str} response{address_info}: Raw='{response}', Value='{response.value}', Unit='{response.unit}', IsNull={response.is_null()}")

        if response.is_null():
            # Logged by _process_individual_obd_response, but good to note here too
            logger.debug(f"Command {original_cmd_name_str} returned a null response{address_info}.")
            return original_cmd_name_str, None, None, True # True for is_error (due to null)
        
        processed_value, unit_str = _process_individual_obd_response(response, original_cmd_name_str)
        
        # If processed_value is None after _process_individual_obd_response (e.g. null or specific handling)
        # consider it an "error" or ignorable state for generic assignment.
        # STATUS and GET_DTC might return non-None processed_value that are complex types.
        is_error_for_value_assignment = False
        if processed_value is None and original_cmd_name_str not in ["STATUS", "GET_DTC", "FUEL_TYPE", "VIN", "ECU_NAME", "FUEL_STATUS", "OBD_COMPLIANCE"]:
             is_error_for_value_assignment = True


        return original_cmd_name_str, processed_value, unit_str, is_error_for_value_assignment

    except Exception as e:
        logger.error(f"Failed to query or process command {original_cmd_name_str}{address_info}: {e}", exc_info=True)
        return original_cmd_name_str, None, None, True # True for is_error

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
        # Map from desired command name (string) to the key in data_to_send dictionary
        output_key_map = {
            "RPM": "rpm", "SPEED": "speed", "COOLANT_TEMP": "coolant_temp",
            "THROTTLE_POS": "throttle_pos", "FUEL_LEVEL": "fuel_level", "ENGINE_LOAD": "engine_load",
            "INTAKE_TEMP": "intake_temp", "MAF": "maf", "FUEL_PRESSURE": "fuel_pressure",
            "FUEL_RAIL_PRESSURE_ABS": "fuel_rail_pressure",
            "FUEL_RAIL_PRESSURE_DIRECT": "fuel_rail_pressure_direct",
            "FUEL_INJECTION_TIMING": "fuel_injection_timing", "FUEL_RATE": "fuel_rate",
            "SHORT_FUEL_TRIM_1": "short_fuel_trim_1", "LONG_FUEL_TRIM_1": "long_fuel_trim_1",
            "SHORT_FUEL_TRIM_2": "short_fuel_trim_2", "LONG_FUEL_TRIM_2": "long_fuel_trim_2",
            "FUEL_TYPE": "fuel_type", "ETHANOL_PERCENT": "ethanol_percent",
            "EVAP_VAPOR_PRESSURE": "evap_vapor_pressure",
            "O2_S1_WR_VOLTAGE": "o2_sensor_1_voltage", "O2_S2_WR_VOLTAGE": "o2_sensor_2_voltage",
            "CATALYST_TEMP_B1S1": "catalyst_temp_b1s1", "CATALYST_TEMP_B2S1": "catalyst_temp_b2s1",
            "EGR_ERROR": "egr_error", "COMMANDED_EGR": "egr_commanded",
            "EVAP_VAPOR_PRESSURE_ABS": "evap_vapor_pressure_abs",
            "AMBIANT_AIR_TEMP": "ambient_air_temp", # Spelling from original
            "OIL_TEMP": "engine_oil_temp", "FUEL_TEMP": "fuel_temp",
            "TIMING_ADVANCE": "timing_advance", "ABSOLUTE_THROTTLE_POS": "abs_throttle_pos",
            "RELATIVE_THROTTLE_POS": "rel_throttle_pos", "ACCELERATOR_POS_D": "accel_pedal_pos",
            "COMMANDED_THROTTLE_ACTUATOR": "commanded_throttle",
            "INTAKE_PRESSURE": "manifold_pressure", "BAROMETRIC_PRESSURE": "baro_pressure",
            "ABSOLUTE_LOAD": "abs_load", "RELATIVE_LOAD": "rel_load",
            "DISTANCE_W_MIL": "distance_with_mil",
            "DISTANCE_SINCE_DTC_CLEAR": "distance_since_codes_cleared",
            "RUN_TIME": "runtime_since_engine_start",
            "TIME_SINCE_DTC_CLEARED": "time_since_codes_cleared",
            "CONTROL_MODULE_VOLTAGE": "control_module_voltage",
            "HYBRID_BATTERY_REMAINING": "hybrid_battery_remaining",
            "ENGINE_FRICTION_PERCENT": "engine_friction_percent",
            "DRIVER_DEMAND_ENGINE_TORQUE": "driver_demand_torque",
            "ACTUAL_ENGINE_TORQUE": "actual_engine_torque",
            "ENGINE_REFERENCE_TORQUE": "engine_ref_torque",
            "CHARGE_AIR_TEMP": "charge_air_temp",
            "VIN": "vin", "ECU_NAME": "ecu_name", "FUEL_STATUS": "fuel_system_status",
            "OBD_COMPLIANCE": "obd_standards",
            # STATUS and GET_DTC are handled specially after gather
        }

        # Define a list of command names (strings) we want to try.
        # Includes standard PIDs and some vehicle info commands. STATUS is included.
        # GET_DTC is handled conditionally later.
        desired_command_names_for_gather = [
            "RPM", "SPEED", "COOLANT_TEMP", "THROTTLE_POS", "FUEL_LEVEL", "ENGINE_LOAD",
            "INTAKE_TEMP", "MAF", "FUEL_PRESSURE", "FUEL_RAIL_PRESSURE_ABS",
            "FUEL_RAIL_PRESSURE_DIRECT", "FUEL_INJECTION_TIMING", "FUEL_RATE",
            "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "SHORT_FUEL_TRIM_2", "LONG_FUEL_TRIM_2",
            "FUEL_TYPE", "ETHANOL_PERCENT", "EVAP_VAPOR_PRESSURE",
            "O2_S1_WR_VOLTAGE", "O2_S2_WR_VOLTAGE", "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1",
            "EGR_ERROR", "COMMANDED_EGR", "EVAP_VAPOR_PRESSURE_ABS", "AMBIANT_AIR_TEMP",
            "OIL_TEMP", "FUEL_TEMP", "TIMING_ADVANCE", "ABSOLUTE_THROTTLE_POS",
            "RELATIVE_THROTTLE_POS", "ACCELERATOR_POS_D", "COMMANDED_THROTTLE_ACTUATOR",
            "INTAKE_PRESSURE", "BAROMETRIC_PRESSURE", "ABSOLUTE_LOAD", "RELATIVE_LOAD",
            "DISTANCE_W_MIL", "DISTANCE_SINCE_DTC_CLEAR", "RUN_TIME", "TIME_SINCE_DTC_CLEARED",
            "CONTROL_MODULE_VOLTAGE", "HYBRID_BATTERY_REMAINING", "ENGINE_FRICTION_PERCENT",
            "DRIVER_DEMAND_ENGINE_TORQUE", "ACTUAL_ENGINE_TORQUE", "ENGINE_REFERENCE_TORQUE",
            "CHARGE_AIR_TEMP",
            "VIN", "ECU_NAME", "FUEL_STATUS", "OBD_COMPLIANCE", "STATUS"
        ]
        
        tasks = []
        commands_to_attempt = [] # Store (cmd_obj, original_name_str)

        for name_str in desired_command_names_for_gather:
            if hasattr(obd.commands, name_str):
                cmd_obj = getattr(obd.commands, name_str)
                commands_to_attempt.append((cmd_obj, name_str))
            else:
                logger.warning(f"OBD command '{name_str}' not found in obd.commands library. Skipping for gather.")
        
        for cmd_obj, original_name in commands_to_attempt:
            tasks.append(query_obd_command(cmd_obj, original_name, client_addr))

        if tasks:
            command_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in command_results:
                if isinstance(result, Exception):
                    # query_obd_command logs its own specific errors.
                    # This is for exceptions from gather itself or unhandled ones in query_obd_command.
                    logger.error(f"Exception during batched OBD query for {client_addr}: {result}", exc_info=result)
                    continue

                original_cmd_name, val, unit, is_error = result
                
                # Even if there's an error or null value, we should still assign NULL explicitly
                # rather than skipping it, so the frontend sees all expected fields
                if is_error and val is None:
                    logger.debug(f"Command {original_cmd_name} returned null, explicitly setting null in response")
                    # Continue to assignment below rather than skipping

                # Handle special commands first
                if original_cmd_name == "STATUS":
                    if isinstance(val, tuple) and len(val) >= 2:
                        data_to_send["mil_on"] = bool(val[0])
                        data_to_send["dtc_count"] = int(val[1])
                    else:
                        logger.warning(f"STATUS command for {client_addr} returned unexpected value: {val}")
                        data_to_send["mil_on"] = False
                        data_to_send["dtc_count"] = 0
                elif original_cmd_name == "VIN":
                    data_to_send["vin"] = val # val is already str from _process_individual_obd_response
                    if val and len(val) == 17:
                        vehicle_info = decode_vin(val)
                        data_to_send["vehicle_make"] = vehicle_info["make"]
                        data_to_send["vehicle_year"] = vehicle_info["model_year"]
                        data_to_send["vehicle_country"] = vehicle_info["country"]
                        logger.debug(f"Decoded VIN: {val} -> Make: {vehicle_info['make']}, Year: {vehicle_info['model_year']}, Country: {vehicle_info['country']}")
                else:
                    # Standard command processing using output_key_map
                    output_key = output_key_map.get(original_cmd_name)
                    if output_key:
                        data_to_send[output_key] = val
                        if unit: # Unit might be None for some (e.g. FUEL_TYPE)
                            data_to_send[f"{output_key}_unit"] = unit
                        # Ensure default units are set if not provided by command and key exists
                        elif f"{output_key}_unit" not in data_to_send and f"{output_key}_unit" in data_to_send: # Check if unit key pre-exists
                             pass # Keep pre-set default unit
                    else:
                        logger.warning(f"No output key mapping found for command: {original_cmd_name} for {client_addr}. Value: {val}")
        
        # Conditionally query GET_DTC based on STATUS results
        if data_to_send.get("mil_on") and data_to_send.get("dtc_count", 0) > 0:
            logger.debug(f"MIL is ON, DTC count: {data_to_send['dtc_count']}. Querying DTCs for {client_addr}...")
            dtc_cmd_obj = getattr(obd.commands, "GET_DTC", None)
            if dtc_cmd_obj:
                # Query GET_DTC as a separate call since it's conditional
                dtc_result_tuple = await query_obd_command(dtc_cmd_obj, "GET_DTC", client_addr)
                # dtc_result_tuple is (original_cmd_name, val, unit, is_error)
                # For GET_DTC, val should be a list of tuples [(CODE, DESCRIPTION), ...]
                if dtc_result_tuple and not dtc_result_tuple[3] and dtc_result_tuple[1] is not None: # not is_error and val is not None
                    dtc_list = dtc_result_tuple[1]
                    data_to_send["dtcs"] = [{"code": dtc[0], "desc": dtc[1]} for dtc in dtc_list if isinstance(dtc, tuple) and len(dtc) == 2]
                elif dtc_result_tuple and dtc_result_tuple[3]: # is_error
                     logger.error(f"Failed to query GET_DTC for {client_addr} (error flag set).")
                else: # val is None or other issue
                     logger.warning(f"GET_DTC query for {client_addr} did not return expected data: {dtc_result_tuple}")
            else:
                logger.warning("GET_DTC command not found in obd.commands library.")

        # Calculate Boost Pressure (dependent on manifold_pressure and baro_pressure from gather)
        intake_pressure_val = data_to_send.get('manifold_pressure')
        baro_pressure_val = data_to_send.get('baro_pressure')

        if intake_pressure_val is not None and baro_pressure_val is not None:
            try:
                calculated_boost = float(intake_pressure_val) - float(baro_pressure_val)
                data_to_send['boost_pressure'] = round(calculated_boost, 2)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Could not calculate boost pressure for {client_addr} due to invalid "
                    f"intake/baro values. Intake: '{intake_pressure_val}', Baro: '{baro_pressure_val}'. Error: {e}"
                )
                data_to_send['boost_pressure'] = None
        else:
            missing_vals_log = []
            if intake_pressure_val is None: missing_vals_log.append("manifold_pressure (intake)")
            if baro_pressure_val is None: missing_vals_log.append("baro_pressure")
            if missing_vals_log:
                 logger.debug(f"Boost pressure not calculated for {client_addr}, missing: {', '.join(missing_vals_log)}.")
            data_to_send['boost_pressure'] = None
            
        data_to_send["status"] = "OK"

    except Exception as e:
        logger.error(f"Error querying OBD or processing data for {client_addr}: {e}", exc_info=True)
        data_to_send["status"] = "OBD_QUERY_ERROR"
        data_to_send["error_details"] = str(e)
    
    return data_to_send