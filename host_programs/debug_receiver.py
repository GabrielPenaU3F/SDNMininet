import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 100))

print("Receiver started")

while True:
    data, addr = sock.recvfrom(4096)
    print(f"Received from {addr}: {data.decode()}")