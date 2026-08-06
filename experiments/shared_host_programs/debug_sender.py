import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dst = ("10.0.0.2", 100)

print("Sender started")

i = 0
t0 = time.monotonic()
while True:
    msg = f"packet {i}"
    print(f"Sending: {msg}")

    try:
        sock.sendto(msg.encode(), dst)
        print("OK")
    except Exception as e:
        print("ERROR:", repr(e))
        raise

    i += 1
    time.sleep(1)