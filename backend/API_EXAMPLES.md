# HUD Backend API Usage Examples

This document provides examples of how to connect to and use the HUD Backend WebSocket API in various programming languages.

## JavaScript (Browser)

```javascript
// Connect to the WebSocket server
let socket = new WebSocket('ws://localhost:8765');

// Handle connection open
socket.addEventListener('open', (event) => {
    console.log('Connected to HUD Backend');
});

// Handle messages from the server
socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    
    // Check status
    if (data.status !== 'OK') {
        console.warn(`OBD Status: ${data.status}`);
        if (data.error_details) {
            console.warn(`Details: ${data.error_details}`);
        }
        // Handle error states
        return;
    }
    
    // Update UI with vehicle data
    updateSpeedometer(data.speed);
    updateTachometer(data.rpm);
    updateTemperature(data.coolant_temp);
    updateFuelGauge(data.fuel_level);
    
    // Check for engine warning light
    if (data.mil_on) {
        showWarningLight();
        showDTCCodes(data.dtcs);
    } else {
        hideWarningLight();
    }
    
    // Display vehicle info
    if (data.vehicle_make) {
        document.getElementById('vehicleInfo').textContent = 
            `${data.vehicle_make} (${data.vehicle_year}) - ${data.vehicle_country}`;
    }
    
    console.log('Full data packet:', data);
});

// Handle errors
socket.addEventListener('error', (event) => {
    console.error('WebSocket error:', event);
});

// Handle connection close
socket.addEventListener('close', (event) => {
    console.log('Connection closed, code:', event.code, 'reason:', event.reason);
    // Try to reconnect after a delay
    setTimeout(() => {
        console.log('Attempting to reconnect...');
        // Recreate the WebSocket connection
        socket = new WebSocket('ws://localhost:8765');
    }, 5000);
});

// Helper functions for updating UI elements
function updateSpeedometer(speed) {
    // Update speedometer display
    document.getElementById('speed').textContent = speed ? `${speed} mph` : 'N/A';
    // Additional code to update a graphical speedometer...
}

function updateTachometer(rpm) {
    // Update tachometer display
    document.getElementById('rpm').textContent = rpm ? `${rpm} rpm` : 'N/A';
    // Additional code to update a graphical tachometer...
}

// Additional UI update functions...
```

## Python

```python
import json
import asyncio
import websockets

async def connect_to_hud():
    """Connect to HUD Backend WebSocket server and process data"""
    uri = "ws://localhost:8765"
    
    while True:  # Reconnection loop
        try:
            async with websockets.connect(uri) as websocket:
                print("Connected to HUD Backend")
                
                while True:  # Message processing loop
                    try:
                        # Wait for data
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        # Check status
                        if data.get('status') != 'OK':
                            print(f"OBD Status: {data.get('status')}")
                            if data.get('error_details'):
                                print(f"Details: {data.get('error_details')}")
                            # Handle error states
                            continue
                        
                        # Process and display data
                        print_vehicle_stats(data)
                        
                        # Example of using specific data points
                        if data.get('mil_on'):
                            print("WARNING: Check Engine Light is ON")
                            print(f"DTC Codes: {data.get('dtcs', [])}")
                        
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed unexpectedly")
                        break
                        
        except Exception as e:
            print(f"Connection error: {e}")
        
        print("Attempting to reconnect in 5 seconds...")
        await asyncio.sleep(5)

def print_vehicle_stats(data):
    """Print key vehicle statistics"""
    print("\n----- Vehicle Statistics -----")
    if data.get('vehicle_make') and data.get('vehicle_year'):
        print(f"Vehicle: {data.get('vehicle_make')} ({data.get('vehicle_year')})")
    
    print(f"Speed: {data.get('speed', 'N/A')} {data.get('speed_unit', 'mph')}")
    print(f"RPM: {data.get('rpm', 'N/A')} {data.get('rpm_unit', 'rpm')}")
    print(f"Engine Temperature: {data.get('coolant_temp', 'N/A')} {data.get('coolant_temp_unit', '°C')}")
    print(f"Fuel Level: {data.get('fuel_level', 'N/A')} {data.get('fuel_level_unit', '%')}")
    print(f"Engine Load: {data.get('engine_load', 'N/A')} {data.get('engine_load_unit', '%')}")
    
    # Print advanced stats if available
    if data.get('intake_temp') is not None:
        print("\n----- Advanced Statistics -----")
        print(f"Intake Temp: {data.get('intake_temp')} {data.get('intake_temp_unit', '°C')}")
        print(f"MAF: {data.get('maf', 'N/A')} {data.get('maf_unit', 'g/s')}")
        print(f"Throttle Position: {data.get('throttle_pos', 'N/A')} {data.get('throttle_pos_unit', '%')}")
        print(f"Oil Temperature: {data.get('engine_oil_temp', 'N/A')} {data.get('engine_oil_temp_unit', '°C')}")

# Run the connection
asyncio.run(connect_to_hud())
```

## Node.js (Server)

```javascript
const WebSocket = require('ws');

// Function to connect to the WebSocket server
function connectToHUD() {
    const ws = new WebSocket('ws://localhost:8765');
    
    // Set up event handlers
    ws.on('open', () => {
        console.log('Connected to HUD Backend');
    });
    
    ws.on('message', (data) => {
        try {
            const vehicleData = JSON.parse(data);
            
            // Check connection status
            if (vehicleData.status !== 'OK') {
                console.log(`OBD Status: ${vehicleData.status}`);
                if (vehicleData.error_details) {
                    console.log(`Details: ${vehicleData.error_details}`);
                }
                return;
            }
            
            // Process vehicle data
            processVehicleData(vehicleData);
            
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    });
    
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
    
    ws.on('close', (code, reason) => {
        console.log(`Connection closed: ${code} - ${reason}`);
        console.log('Attempting to reconnect in 5 seconds...');
        
        // Reconnect after delay
        setTimeout(connectToHUD, 5000);
    });
    
    return ws;
}

// Function to process vehicle data
function processVehicleData(data) {
    console.log('\n--- Vehicle Data Update ---');
    
    // Core engine data
    console.log(`Speed: ${data.speed !== null ? data.speed : 'N/A'} ${data.speed_unit || 'mph'}`);
    console.log(`RPM: ${data.rpm !== null ? data.rpm : 'N/A'} ${data.rpm_unit || 'rpm'}`);
    console.log(`Engine Temp: ${data.coolant_temp !== null ? data.coolant_temp : 'N/A'} ${data.coolant_temp_unit || '°C'}`);
    
    // Engine performance
    if (data.engine_load !== null) {
        console.log(`\nEngine Performance:`);
        console.log(`Load: ${data.engine_load} ${data.engine_load_unit || '%'}`);
        
        if (data.actual_engine_torque !== null) {
            console.log(`Torque: ${data.actual_engine_torque} ${data.actual_engine_torque_unit || '%'}`);
        }
    }
    
    // Check for MIL (Check Engine Light)
    if (data.mil_on) {
        console.log('\n⚠️ CHECK ENGINE LIGHT ON ⚠️');
        console.log(`DTC Count: ${data.dtc_count}`);
        
        if (data.dtcs && data.dtcs.length > 0) {
            console.log('Diagnostic Trouble Codes:');
            data.dtcs.forEach(dtc => {
                console.log(`- ${dtc.code}: ${dtc.desc}`);
            });
        }
    }
    
    // Vehicle identification
    if (data.vehicle_make) {
        console.log(`\nVehicle: ${data.vehicle_make} (${data.vehicle_year})`);
        console.log(`Origin: ${data.vehicle_country || 'Unknown'}`);
    }
}

// Start the connection
const wsClient = connectToHUD();

// Handle process termination
process.on('SIGINT', () => {
    console.log('Closing connection and exiting...');
    wsClient.close();
    process.exit(0);
});
```

## Java

```java
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Map;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import org.json.JSONObject;

public class HUDBackendClient {
    
    private WebSocketClient webSocketClient;
    
    public HUDBackendClient() {
        initWebSocketClient();
    }
    
    private void initWebSocketClient() {
        try {
            URI serverUri = new URI("ws://localhost:8765");
            
            webSocketClient = new WebSocketClient(serverUri) {
                @Override
                public void onOpen(ServerHandshake handshakedata) {
                    System.out.println("Connected to HUD Backend");
                }
                
                @Override
                public void onMessage(String message) {
                    try {
                        JSONObject data = new JSONObject(message);
                        
                        // Check connection status
                        String status = data.optString("status");
                        if (!"OK".equals(status)) {
                            System.out.println("OBD Status: " + status);
                            if (data.has("error_details") && !data.isNull("error_details")) {
                                System.out.println("Details: " + data.getString("error_details"));
                            }
                            return;
                        }
                        
                        // Process the data
                        processVehicleData(data);
                        
                    } catch (Exception e) {
                        System.err.println("Error processing message: " + e.getMessage());
                    }
                }
                
                @Override
                public void onClose(int code, String reason, boolean remote) {
                    System.out.println("Connection closed: " + reason + " (Code: " + code + ")");
                    
                    // Attempt to reconnect after delay
                    System.out.println("Attempting to reconnect in 5 seconds...");
                    try {
                        Thread.sleep(5000);
                        initWebSocketClient();
                    } catch (InterruptedException e) {
                        System.err.println("Reconnection interrupted: " + e.getMessage());
                    }
                }
                
                @Override
                public void onError(Exception ex) {
                    System.err.println("WebSocket error: " + ex.getMessage());
                }
            };
            
            webSocketClient.connect();
            
        } catch (URISyntaxException e) {
            System.err.println("Invalid server URI: " + e.getMessage());
        }
    }
    
    private void processVehicleData(JSONObject data) {
        System.out.println("\n----- Vehicle Data Update -----");
        
        // Basic vehicle data
        System.out.println("Speed: " + formatValue(data, "speed", "mph"));
        System.out.println("RPM: " + formatValue(data, "rpm", "rpm"));
        System.out.println("Coolant Temperature: " + formatValue(data, "coolant_temp", "°C"));
        System.out.println("Fuel Level: " + formatValue(data, "fuel_level", "%"));
        
        // Check engine light
        boolean milOn = data.optBoolean("mil_on", false);
        if (milOn) {
            System.out.println("\n⚠️ CHECK ENGINE LIGHT ON ⚠️");
            int dtcCount = data.optInt("dtc_count", 0);
            System.out.println("DTC Count: " + dtcCount);
            
            // Display DTCs if available
            if (data.has("dtcs") && !data.isNull("dtcs")) {
                System.out.println("Diagnostic Trouble Codes:");
                for (int i = 0; i < data.getJSONArray("dtcs").length(); i++) {
                    JSONObject dtc = data.getJSONArray("dtcs").getJSONObject(i);
                    System.out.println("- " + dtc.getString("code") + ": " + dtc.getString("desc"));
                }
            }
        }
        
        // Vehicle identification
        if (data.has("vehicle_make") && !data.isNull("vehicle_make")) {
            System.out.println("\nVehicle Information:");
            System.out.println("Make: " + data.optString("vehicle_make", "Unknown"));
            System.out.println("Year: " + data.optString("vehicle_year", "Unknown"));
            System.out.println("Country: " + data.optString("vehicle_country", "Unknown"));
        }
    }
    
    private String formatValue(JSONObject data, String key, String unit) {
        if (data.has(key) && !data.isNull(key)) {
            Object value = data.get(key);
            String unitValue = data.has(key + "_unit") ? data.getString(key + "_unit") : unit;
            return value + " " + unitValue;
        }
        return "N/A";
    }
    
    public void disconnect() {
        if (webSocketClient != null) {
            webSocketClient.close();
        }
    }
    
    public static void main(String[] args) {
        HUDBackendClient client = new HUDBackendClient();
        
        // Add shutdown hook to close connection on exit
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down...");
            client.disconnect();
        }));
    }
}
```

## C# (.NET)

```csharp
using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Text.Json;

class HUDBackendClient
{
    private ClientWebSocket webSocket;
    private bool shouldReconnect = true;
    private CancellationTokenSource cts;
    
    public async Task ConnectAsync()
    {
        cts = new CancellationTokenSource();
        
        while (shouldReconnect)
        {
            try
            {
                using (webSocket = new ClientWebSocket())
                {
                    Uri serverUri = new Uri("ws://localhost:8765");
                    
                    Console.WriteLine("Connecting to HUD Backend...");
                    await webSocket.ConnectAsync(serverUri, cts.Token);
                    Console.WriteLine("Connected to HUD Backend");
                    
                    await ReceiveDataLoop();
                }
            }
            catch (WebSocketException ex)
            {
                Console.WriteLine($"WebSocket error: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            
            if (shouldReconnect)
            {
                Console.WriteLine("Attempting to reconnect in 5 seconds...");
                await Task.Delay(5000);
            }
        }
    }
    
    private async Task ReceiveDataLoop()
    {
        var buffer = new byte[8192];
        
        while (webSocket.State == WebSocketState.Open)
        {
            try
            {
                WebSocketReceiveResult result = await webSocket.ReceiveAsync(
                    new ArraySegment<byte>(buffer), cts.Token);
                
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await webSocket.CloseAsync(
                        WebSocketCloseStatus.NormalClosure, 
                        "Closing", 
                        cts.Token);
                    break;
                }
                
                // Get the message
                string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                ProcessMessage(message);
            }
            catch (WebSocketException ex)
            {
                Console.WriteLine($"WebSocket receive error: {ex.Message}");
                break;
            }
        }
    }
    
    private void ProcessMessage(string message)
    {
        try
        {
            using (JsonDocument doc = JsonDocument.Parse(message))
            {
                JsonElement root = doc.RootElement;
                
                // Check status
                string status = root.GetProperty("status").GetString();
                if (status != "OK")
                {
                    Console.WriteLine($"OBD Status: {status}");
                    if (root.TryGetProperty("error_details", out JsonElement errorDetails) && errorDetails.ValueKind != JsonValueKind.Null)
                    {
                        Console.WriteLine($"Details: {errorDetails.GetString()}");
                    }
                    return;
                }
                
                DisplayVehicleData(root);
            }
        }
        catch (JsonException ex)
        {
            Console.WriteLine($"Error parsing JSON: {ex.Message}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error processing message: {ex.Message}");
        }
    }
    
    private void DisplayVehicleData(JsonElement data)
    {
        Console.WriteLine("\n===== Vehicle Data Update =====");
        
        // Basic vehicle stats
        DisplayValue(data, "speed", "Speed", "mph");
        DisplayValue(data, "rpm", "RPM", "rpm");
        DisplayValue(data, "coolant_temp", "Coolant Temp", "°C");
        DisplayValue(data, "fuel_level", "Fuel Level", "%");
        DisplayValue(data, "engine_load", "Engine Load", "%");
        
        // Check engine light
        if (data.TryGetProperty("mil_on", out JsonElement milOn) && milOn.GetBoolean())
        {
            Console.WriteLine("\n⚠️ CHECK ENGINE LIGHT ON ⚠️");
            
            if (data.TryGetProperty("dtc_count", out JsonElement dtcCount))
            {
                Console.WriteLine($"DTC Count: {dtcCount.GetInt32()}");
            }
            
            // Display DTCs if available
            if (data.TryGetProperty("dtcs", out JsonElement dtcs) && dtcs.ValueKind == JsonValueKind.Array)
            {
                Console.WriteLine("Diagnostic Trouble Codes:");
                foreach (JsonElement dtc in dtcs.EnumerateArray())
                {
                    string code = dtc.GetProperty("code").GetString();
                    string desc = dtc.GetProperty("desc").GetString();
                    Console.WriteLine($"- {code}: {desc}");
                }
            }
        }
        
        // Vehicle identification
        if (data.TryGetProperty("vehicle_make", out JsonElement make) && 
            make.ValueKind != JsonValueKind.Null)
        {
            Console.WriteLine("\nVehicle Information:");
            Console.WriteLine($"Make: {make.GetString()}");
            
            if (data.TryGetProperty("vehicle_year", out JsonElement year) && 
                year.ValueKind != JsonValueKind.Null)
            {
                Console.WriteLine($"Year: {year.GetInt32()}");
            }
            
            if (data.TryGetProperty("vehicle_country", out JsonElement country) && 
                country.ValueKind != JsonValueKind.Null)
            {
                Console.WriteLine($"Country: {country.GetString()}");
            }
        }
    }
    
    private void DisplayValue(JsonElement data, string key, string label, string defaultUnit)
    {
        if (data.TryGetProperty(key, out JsonElement value) && 
            value.ValueKind != JsonValueKind.Null)
        {
            string unitValue = defaultUnit;
            if (data.TryGetProperty($"{key}_unit", out JsonElement unit) && 
                unit.ValueKind != JsonValueKind.Null)
            {
                unitValue = unit.GetString();
            }
            
            string displayValue = value.ValueKind == JsonValueKind.Number ? 
                value.GetDouble().ToString() : value.ToString();
                
            Console.WriteLine($"{label}: {displayValue} {unitValue}");
        }
    }
    
    public void Disconnect()
    {
        shouldReconnect = false;
        cts?.Cancel();
    }
    
    public static async Task Main(string[] args)
    {
        HUDBackendClient client = new HUDBackendClient();
        
        // Setup cancellation for Ctrl+C
        Console.CancelKeyPress += (sender, e) => {
            Console.WriteLine("Closing connection and exiting...");
            client.Disconnect();
            e.Cancel = true;
        };
        
        await client.ConnectAsync();
    }
}
```

## Integration with Common UI Frameworks

### React.js Example

```jsx
import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';

function Dashboard() {
    const [vehicleData, setVehicleData] = useState({
        speed: null,
        rpm: null,
        coolant_temp: null,
        fuel_level: null,
        throttle_pos: null,
        engine_load: null,
        mil_on: false,
        dtcs: [],
        status: null,
        error_details: null,
        vehicle_make: null,
        vehicle_year: null,
        vehicle_country: null
    });
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState(null);
    const wsRef = useRef(null);
    
    useEffect(() => {
        // Connect to WebSocket
        connectWebSocket();
        
        // Clean up on unmount
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);
    
    const connectWebSocket = () => {
        const ws = new WebSocket('ws://localhost:8765');
        wsRef.current = ws;
        
        ws.onopen = () => {
            console.log('Connected to HUD Backend');
            setConnected(true);
            setError(null);
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setVehicleData(data);
            } catch (err) {
                console.error('Error parsing WebSocket message:', err);
            }
        };
        
        ws.onerror = (event) => {
            console.error('WebSocket error:', event);
            setError('Connection error');
        };
        
        ws.onclose = (event) => {
            console.log('WebSocket connection closed', event.code, event.reason);
            setConnected(false);
            
            // Attempt to reconnect after a delay
            setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 5000);
        };
    };
    
    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <h1>Vehicle Dashboard</h1>
                <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
                    {connected ? 'Connected' : 'Disconnected'}
                </div>
                {error && <div className="error-message">{error}</div>}
                {vehicleData.status && vehicleData.status !== 'OK' && (
                    <div className="status-message">OBD Status: {vehicleData.status}</div>
                )}
                {vehicleData.status && vehicleData.status !== 'OK' && vehicleData.error_details && (
                    <div className="status-message error-details">Details: {vehicleData.error_details}</div>
                )}
            </header>
            
            <div className="vehicle-info">
                {vehicleData.vehicle_make && (
                    <h2>{vehicleData.vehicle_make} ({vehicleData.vehicle_year})</h2>
                )}
                {vehicleData.vehicle_country && <p>Country: {vehicleData.vehicle_country}</p>}
            </div>
            
            <div className="gauges-container">
                <div className="gauge speedometer">
                    <h3>Speed</h3>
                    <div className="gauge-value">{vehicleData.speed || 'N/A'}</div>
                    <div className="gauge-unit">mph</div>
                </div>
                
                <div className="gauge tachometer">
                    <h3>RPM</h3>
                    <div className="gauge-value">{vehicleData.rpm || 'N/A'}</div>
                    <div className="gauge-unit">rpm</div>
                </div>
                
                <div className="gauge temperature">
                    <h3>Temperature</h3>
                    <div className="gauge-value">{vehicleData.coolant_temp || 'N/A'}</div>
                    <div className="gauge-unit">°C</div>
                </div>
                
                <div className="gauge fuel">
                    <h3>Fuel</h3>
                    <div className="gauge-value">{vehicleData.fuel_level || 'N/A'}</div>
                    <div className="gauge-unit">%</div>
                </div>
            </div>
            
            {vehicleData.mil_on && (
                <div className="warning-panel">
                    <h3>⚠️ CHECK ENGINE LIGHT ON</h3>
                    <p>DTC Count: {vehicleData.dtc_count}</p>
                    {vehicleData.dtcs.length > 0 && (
                        <ul className="dtc-list">
                            {vehicleData.dtcs.map((dtc, index) => (
                                <li key={index}><strong>{dtc.code}:</strong> {dtc.desc}</li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
            
            <div className="additional-data">
                <h3>Additional Vehicle Data</h3>
                <div className="data-grid">
                    <div className="data-item">
                        <span className="label">Throttle Position:</span>
                        <span className="value">{vehicleData.throttle_pos || 'N/A'} %</span>
                    </div>
                    <div className="data-item">
                        <span className="label">Engine Load:</span>
                        <span className="value">{vehicleData.engine_load || 'N/A'} %</span>
                    </div>
                    {/* Additional data items can be added here */}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
```

## Notes on Usage

### Best Practices

1. **Reconnection Logic**: Always implement reconnection logic to handle unexpected disconnections.
2. **Error Handling**: Check the `status` field in each response to detect connection problems.
3. **Null Checking**: Not all vehicles support all parameters - always check if values are null.
4. **Unit Display**: Include the unit when displaying values for better user experience.
5. **Rate Limiting**: Consider the update frequency when designing your UI to avoid performance issues.

### Performance Considerations

- The HUD Backend sends updates at a configurable interval (default 0.5 seconds).
- For mobile or web applications, consider buffering or throttling updates to reduce CPU usage.
- UI animations should be optimized to prevent jerky updates when receiving data.