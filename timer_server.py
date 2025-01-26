import socket
import time

# Setup server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
server_socket.bind(("127.0.0.1", 12345))  # Bind to localhost and port 12345

print("Press Enter to broadcast the start signal...")
input()  # Wait for Enter key to start the stopwatches
start_time = time.time()

# Broadcast start signal to all clients on the network
message = f"START,{start_time}".encode()
server_socket.sendto(message, ('<broadcast>', 12345))  # Broadcast message to all on port 12345
print(f"Start signal sent at {start_time}")
server_socket.close()

print(f"Start signal sent to broadcast on port 12345")
