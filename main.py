import cv2
import socket
import pickle
import struct

    # Connect to the Raspberry Pi
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '192.168.240.16' # Replace with your Pi's IP address
port = 9999
client_socket.connect((host_ip, port))

data = b""
payload_size = struct.calcsize("L")

while True:
    while len(data) < payload_size:
        packet = client_socket.recv(4096) # Adjust buffer size as needed
        if not packet:
            break
        data += packet

    if not packet:
        break

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096) # Adjust buffer size as needed

    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)

    cv2.imshow('Received Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client_socket.close()
cv2.destroyAllWindows()
