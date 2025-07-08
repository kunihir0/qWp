# QWP HUD - OBD Data Dashboard

A real-time dashboard for displaying OBD (On-Board Diagnostics) data from vehicles using Vue 3 and WebSockets.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
# Install dependencies
npm install

# Copy the example environment file
cp .env.example .env

# Edit the .env file to configure the WebSocket connection if needed
```

### WebSocket Configuration

The dashboard connects to a WebSocket server to receive real-time OBD data. By default, it connects to `ws://localhost:8765`. You can change this by setting the `VITE_WS_URL` environment variable in the `.env` file.

```
# .env
VITE_WS_URL=ws://your-backend-server:port
```

### Connection Handling

The frontend implements robust WebSocket connection handling:

- Automatic reconnection with exponential backoff
- Proper error handling for connection issues
- Data validation to ensure proper message format
- Status tracking with visual indicators

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

## Data Format

The backend sends OBD data in JSON format through the WebSocket connection. The frontend expects data to match the `OBDData` interface defined in App.vue, which includes:

- Core engine parameters (RPM, speed, throttle position, etc.)
- Fuel system data
- Temperature readings
- Emissions data including DTCs (Diagnostic Trouble Codes)
- Vehicle information

## Recent Updates

- Improved WebSocket connection handling with exponential backoff
- Added environment variable support for WebSocket URL configuration
- Enhanced error handling for malformed data
- Better reconnection logic with user feedback
