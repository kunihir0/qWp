import socket
import time

# ELM327-emulator must be running with: elm -s car -n 35000
HOST = "localhost"
PORT = 35000
CONNECTION_DESCRIPTION = f"raw socket to {HOST}:{PORT}"

print(f"Attempting to connect to {CONNECTION_DESCRIPTION}")

try:
    # Using a raw socket directly.
    # This bypasses pyserial's URL handling and its serial parameter emulation for sockets.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3.0)  # Set a timeout for socket operations (e.g., connect, recv)
        print(f"Connecting raw socket to {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print(f"Raw socket connected to {HOST}:{PORT}.")

        def send_and_receive(sock, command_str, command_desc, delay=0.5, read_len=1024):
            """Sends a command string (adds \r) and tries to read a response."""
            command_bytes = (command_str + "\r").encode('ascii')
            print(f"\n--- Testing: {command_desc} ---")
            print(f"Sending: {command_bytes!r}")
            try:
                sock.sendall(command_bytes)
                time.sleep(delay)  # Wait for the emulator to process and respond
                response_bytes = sock.recv(read_len)
                print(f"Received: {response_bytes!r}")
                if response_bytes:
                    try:
                        print(f"Decoded: {response_bytes.decode('ascii').strip()}")
                    except UnicodeDecodeError:
                        print("Decoded: (Contains non-ASCII bytes)")
                return response_bytes
            except socket.timeout:
                print("Receive timed out.")
                return b''
            except Exception as e_send_recv:
                print(f"Error during send/receive for {command_desc}: {e_send_recv}")
                return b''

        # Give a moment for the connection to be fully accepted by the emulator
        time.sleep(0.5)

        # Test 1: Send ATZ (reset ELM)
        # Expected: Emulator might echo ATZ, then send its version or just '>'
        response_atz = send_and_receive(s, "ATZ", "ATZ (Reset)")

        # Test 2: Send ATE0 (echo off - good practice)
        # Expected: ATE0 (if echo was on), then OK, then '>'
        response_ate0 = send_and_receive(s, "ATE0", "ATE0 (Echo Off)")
        
        # Test 3: Send ATL0 (linefeeds off - good practice)
        # Expected: ATL0 (if echo was on), then OK, then '>'
        response_atl0 = send_and_receive(s, "ATL0", "ATL0 (Linefeeds Off)")

        # Test 4: Send ATI (get ELM ID/Version)
        # Expected: ELM327 vX.X, then '>'
        response_ati = send_and_receive(s, "ATI", "ATI (Adapter Version)")

        # Test 5: Send 0100 (Supported PIDs Mode 01, PIDs 01-20)
        # Expected: A response like 41 00 XX XX XX XX, then '>'
        # The ELM327-emulator with 'scenario car' should provide a response.
        response_0100 = send_and_receive(s, "0100", "0100 (Supported PIDs)", delay=1.0)

        # Test 6: Send ATDP (Describe Protocol)
        # Expected: AUTO, ISO 15765-4 (CAN 11/500) or similar, then '>'
        response_atdp = send_and_receive(s, "ATDP", "ATDP (Describe Protocol)")


except socket.timeout:
    print(f"Raw Socket - Connection to {HOST}:{PORT} timed out.")
except socket.error as e:
    print(f"Raw Socket - Socket error: {e}")
except Exception as e:
    print(f"Raw Socket - Other error: {e}")

print("\nRaw socket test finished.")
