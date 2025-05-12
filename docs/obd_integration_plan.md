# OBD Integration Plan for HUD Backend

## 1. Objective

The primary goal is to modify the Python backend (`backend/main.py`) to transition from its current internal RPM and Speed data simulation to utilizing live data queried from a connected OBD (On-Board Diagnostics) emulator, such as an ELM327. The speed data must be converted and reported in Miles Per Hour (MPH). This modification is a crucial step towards developing a reliable Heads-Up Display (HUD) system for real-world vehicle application, where data accuracy, responsiveness, and resilience are paramount.

## 2. Modifications to `stream_obd_data_to_client` function in `backend/main.py`

The core changes will occur within the `async def stream_obd_data_to_client(websocket):` function.

### Step 1: Remove Internal Simulation Logic

*   **Action:** Comment out or entirely remove the existing simulation code block.
*   **Details:** This includes the `current_rpm`, `current_speed_mph`, `simulation_phase`, and `phase_timer` variable initializations (around lines 137-140) and the conditional logic (`if simulation_phase == "idle":`, `elif simulation_phase == "accelerating":`, etc.) that updates these variables (approximately lines 150-194). The `SIMULATION_STEP_INTERVAL` (line 141) might be repurposed or a new interval for OBD polling will be defined.

    ```python
    # # Simulator state variables
    # current_rpm = 800.0
    # current_speed_mph = 0.0
    # simulation_phase = "idle"  # "idle", "accelerating", "cruising", "decelerating"
    # phase_timer = 0  # Counter for steps within a phase
    # SIMULATION_STEP_INTERVAL = 0.5 # Corresponds to await asyncio.sleep()

    # ...
    #                 # Simulation Logic
    #                 phase_timer += 1
    #
    #                 if simulation_phase == "idle":
    # # ... (rest of simulation logic) ...
    #                 elif simulation_phase == "decelerating":
    # # ... (rest of simulation logic) ...
    #
    #                 # Ensure values are within reasonable bounds and rounded
    #                 current_speed_mph = max(0.0, round(current_speed_mph, 2))
    #                 current_rpm = max(600.0, round(current_rpm, 2)) # Min idle RPM
    ```

### Step 2: Query Live OBD Data

*   **Action:** Implement logic to query live RPM and Speed data using the global `obd_connection` object.
*   **Details:**
    *   Ensure `obd_connection` is valid and connected before attempting queries:
        ```python
        if obd_connection and obd_connection.is_connected() and obd_connection.protocol_id():
            # Proceed with queries
            pass
        else:
            # Handle OBD not connected (e.g., send error, log, attempt reconnect)
            logger.warning("OBD not connected or protocol not set. Skipping data query.")
            # Potentially send a status update to the client
            data_to_send = {
                "rpm": 0, "rpm_unit": "rpm",
                "speed": 0, "speed_unit": "MPH",
                "status": "OBD_DISCONNECTED"
            }
            # Add a delay before next attempt to avoid busy-looping
            await asyncio.sleep(2) # Configurable delay
            continue # Skip to next iteration of the loop
        ```
    *   Query RPM:
        ```python
        rpm_response = obd_connection.query(obd.commands.RPM)
        if not rpm_response.is_null() and rpm_response.value is not None:
            # Assuming rpm_response.value is a pint.Quantity
            current_rpm = round(rpm_response.value.magnitude, 2)
        else:
            current_rpm = 0 # Or a previous valid value, or specific error indicator
            logger.warning("Failed to retrieve RPM or RPM is null.")
        ```
    *   Query Speed:
        ```python
        speed_response = obd_connection.query(obd.commands.SPEED)
        # Speed conversion will be handled in the next step
        ```

### Step 3: Speed Unit Conversion (KMPH to MPH)

*   **Action:** Convert the speed data obtained from `obd.commands.SPEED` (typically in KMPH) to MPH.
*   **Details:**
    *   The `obd.commands.SPEED` command usually returns data as a `pint.Quantity` object in kilometers per hour (km/h).
    *   Conversion formula: 1 KMPH = 0.621371 MPH.
    *   Implementation:
        ```python
        current_speed_kmph = 0.0
        if not speed_response.is_null() and speed_response.value is not None:
            # Assuming speed_response.value is a pint.Quantity in KMPH
            current_speed_kmph = speed_response.value.magnitude
        else:
            logger.warning("Failed to retrieve Speed or Speed is null.")

        # Convert KMPH to MPH
        conversion_factor_kmph_to_mph = 0.621371
        current_speed_mph = round(current_speed_kmph * conversion_factor_kmph_to_mph, 2)
        ```

### Step 4: Data Packaging for WebSocket

*   **Action:** Populate the `data_to_send` dictionary with the live RPM and converted Speed (MPH) values.
*   **Details:**
    ```python
    data_to_send = {
        "rpm": current_rpm,
        "rpm_unit": "rpm", # Or rpm_response.unit if available and desired
        "speed": current_speed_mph,
        "speed_unit": "MPH", # Explicitly set to MPH after conversion
        "status": "OK" # Add a status field
    }
    json_payload = json.dumps(data_to_send)
    logger.debug(f"Sending to {client_addr}: {json_payload}")
    await websocket.send(json_payload)
    ```
    *   The polling interval (currently `SIMULATION_STEP_INTERVAL`) should be adjusted based on desired responsiveness and OBD adapter capabilities. A common interval is 0.1 to 0.5 seconds.
        ```python
        OBD_POLLING_INTERVAL = 0.2 # seconds
        await asyncio.sleep(OBD_POLLING_INTERVAL)
        ```

## 3. Data Extraction Notes

*   The `python-obd` library returns values for commands like `RPM` and `SPEED` as `pint.Quantity` objects.
*   To get the numerical value, use the `.magnitude` attribute (e.g., `rpm_response.value.magnitude`).
*   To get the unit, use the `.units` attribute (e.g., `rpm_response.value.units`), though for this plan, we are standardizing units in the output ("rpm", "MPH").
*   Always check if a response is null using `response.is_null()` before accessing `.value`.

## 4. Future Considerations / Next Steps (Tailored for Real-World HUD)

Given the intended use in a real-world vehicle HUD, the following aspects are critical for future development:

*   **Data Smoothing & Filtering:**
    *   **Need:** Live OBD data, especially RPM and Speed, can be noisy or fluctuate rapidly due to sensor characteristics or transient vehicle states. This can lead to a jittery and distracting HUD display.
    *   **Techniques:**
        *   **Moving Averages (Simple, Weighted, Exponential):** Relatively easy to implement. A simple moving average can smooth out rapid fluctuations. Exponential moving averages give more weight to recent data, improving responsiveness.
        *   **Kalman Filters:** More complex but highly effective for estimating the true state of a system from noisy sensor measurements. Ideal for applications requiring high accuracy and responsiveness, but has a higher implementation and computational overhead.
    *   **Trade-offs:** Consider the balance between smoothness (reducing jitter) and responsiveness (quickly reflecting actual changes in vehicle state). Over-smoothing can introduce lag.

*   **Latency Optimization:**
    *   **Concern:** Minimize the delay from when data is generated by the vehicle's ECU, read by the OBD adapter, processed by `backend/main.py`, and finally displayed on the HUD.
    *   **Strategies:**
        *   **Efficient OBD Queries:** Use `fast=True` in `obd.OBD()` if supported and stable, though current setup uses `fast=False`. Batch queries if possible (though `python-obd` handles this to some extent).
        *   **Optimized Python Code:** Ensure the data processing loop in `stream_obd_data_to_client` is efficient. Avoid blocking operations.
        *   **WebSocket Performance:** Ensure WebSocket communication is not a bottleneck. Consider message batching if sending very high-frequency updates, though individual RPM/Speed updates are likely fine.
        *   **Frontend Rendering:** Optimize the HUD display rendering logic.

*   **Error Handling & Resilience:**
    *   **Criticality:** The system must be robust to OBD connection issues (disconnects, timeouts, adapter errors, invalid data packets).
    *   **Implementation:**
        *   **Connection Monitoring:** Continuously check `obd_connection.is_connected()`.
        *   **Reconnection Logic:** Implement an automatic reconnection strategy with backoff delays if the connection is lost.
        *   **Status Indication:** Provide clear status (e.g., "Connecting...", "Disconnected", "Data Error") to the HUD so the driver is aware of the data feed's state.
        *   **Timeout Handling:** Implement timeouts for OBD queries to prevent indefinite blocking. `python-obd` has some internal timeouts, but application-level checks might be needed.

*   **Data Validation:**
    *   **Need:** OBD adapters or vehicle ECUs can occasionally send erroneous or out-of-range data (e.g., RPM of 20000, Speed of 500 MPH).
    *   **Checks:** Implement sanity checks for received data. For example, RPM should be within a plausible range (e.g., 0-10000), Speed within (e.g., 0-200 MPH).
    *   **Action:** If invalid data is detected, either discard it, use the last known good value, or indicate an error on the HUD.

*   **Performance Monitoring:**
    *   **Concern:** As more OBD parameters are potentially added, or if processing logic becomes more complex (e.g., advanced filtering), the Python backend's performance must be monitored.
    *   **Action:** Ensure the `asyncio` event loop is not being blocked and that the backend can maintain the desired data refresh rate for the HUD without excessive CPU/memory usage. Profile the application if performance issues arise.

*   **Configuration:**
    *   **Need:** Make key parameters easily configurable rather than hardcoded.
    *   **Parameters:**
        *   OBD connection details (e.g., port/host for socket connections, serial port path, baudrate for serial).
        *   Polling intervals.
        *   Smoothing algorithm parameters (e.g., window size for moving average).
        *   Data validation ranges.
    *   **Method:** Use a configuration file (e.g., JSON, YAML, INI) or environment variables.