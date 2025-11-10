import cv2
import socket
import pickle
import struct

# Initialize the camera
camera = cv2.VideoCapture(0) # 0 for the first camera, adjust if needed
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

# Create a socket for streaming
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name) # Or use your Pi's static IP
port = 9999
socket_address = (host_ip, port)

server_socket.bind(socket_address)
server_socket.listen(5)
print(f"Listening at {socket_address}")

client_socket, addr = server_socket.accept()
print(f"Got connection from {addr}")

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # Serialize frame
    data = pickle.dumps(frame)

    # Send message size
    message_size = struct.pack("L", len(data))

    # Send frame data
    client_socket.sendall(message_size + data)

    # Optional: Display frame on Pi (for testing)
    # cv2.imshow('Raspberry Pi Stream', frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

camera.release()
client_socket.close()
server_socket.close()
cv2.destroyAllWindows()
