import socket

# Setup server
host = '0.0.0.0'    # Listen on all available interfaces
port = 12345        # Change to same port on arduino

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))

print(f"Listening on {host}:{port}...")

while True:
  client_socket, addr = server_socket.accept()
  print(f"Connection from {addr}")

  data = client_socket.recv(1024).decode('utf-8')
  if data:
    print(f"Received: {data}")

  client_socket.close(0
