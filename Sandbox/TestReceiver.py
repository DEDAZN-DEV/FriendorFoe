import socket

PORT = 2222

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), PORT))

sock.listen(5)

while True:
    (conn, address) = sock.accept()
    data = conn.recv(16)
    print("Received data from: " + str(address) + ' ' + data)
