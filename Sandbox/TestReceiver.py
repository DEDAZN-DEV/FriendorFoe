import socket
import sys

import serial
import serial.tools.list_ports

HOST = ''
PORT = 7777


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((HOST, PORT))
    except socket.error as emsg1:
        print(emsg1)
        sys.exit()

    sock.listen(5)

    print("SERIAL TESTING...Please Wait.")

    print(serial_debug())

    print("TESTING COMPLETE...")

    print("SERVER ESTABLISHED...")

    while True:
        (conn, address) = sock.accept()
        data = conn.recv(64)

        try:
            print("Received data from: " + conn.getpeername().__str__() + '\t\t' + data.__str__())
        except TypeError as emsg2:
            print(emsg2)
            sys.exit()


def serial_debug():
    list = serial.tools.list_ports.comports()
    available = []
    for port in list:
        available.append(port.device)

    return available


main()
