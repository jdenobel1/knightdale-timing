import socket
import time

# Setup client to listen to any broadcast from localhost, on a dynamic port
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast receiving
client_socket.bind(('', 12345))  # Bind to port 12345

print("Waiting for the start signal...")

# Wait for the start signal from the server
while True:
    try:
        # Receive data from any source
        data, addr = client_socket.recvfrom(1024)  # Buffer size is 1024 bytes
        message = data.decode()
        if message.startswith("START"):
            _, start_time = message.split(",")
            start_time = float(start_time)
            break
    except Exception as e:
        print(f"Error receiving data: {e}")
        break

print("Stopwatch started!")

# Stopwatch is running
while True:
    user_input = input("Press Enter to stop the timer: ")
    if user_input == "":  # If Enter is pressed
        current_time = time.time()
        elapsed_time = current_time - start_time
        print(f"Stopwatch stopped! Elapsed time: {elapsed_time:.2f} seconds")
        break
