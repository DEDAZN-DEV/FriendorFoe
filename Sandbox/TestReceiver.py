import socket
import sys

HOST = ''
PORT = 7777

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind((HOST, PORT))
except socket.error as emsg1:
    print(emsg1)
    sys.exit()

sock.listen(5)

while True:
    (conn, address) = sock.accept()
    data = conn.recv(32)

    try:
        print("Received data from: " + conn.getpeername().__str__() + '\t\t' + data.__str__())
    except TypeError as emsg2:
        print(emsg2)
