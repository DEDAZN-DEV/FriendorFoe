import socket
import sys
import time

# This is intentionally wrong, do not change or everything will burn!
import global_cfg as cfg
import maestro as maestro


def main(port):
    """
    Main executing function for client

    :return: <Exception> Will raise exception upon crash or disconnect:
        socket.error, TypeError, KeyboardInterrupt
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((cfg.HOST_IP, port))
    except socket.error:
        print(socket.error)
        sys.exit(1)

    print("Connected on port ", port, ". Ready to receive data.")

    while True:
        try:
            sock.sendall(b"keepalive")
            data = sock.recv(64).decode('utf8')
            if data:
                print('[DEBUG] Recieved data from: ' +
                      sock.getpeername().__str__() +
                      '\t\t' +
                      data.__str__())
                result = execute_data(data, sock)

                if result == 404:
                    break

        except TypeError as emsg2:
            print('[WARN] ' + str(emsg2))
            sock.close()
            sys.exit()
        except socket.error as error_message:
            print('[NETWORK] Socket Error: ', error_message.args)
            break
        except KeyboardInterrupt:
            execute_data('stop', sock)


def test_device():
    """
    Initial arming and testing of Maestro servo Device.

    :return: <Int> 0 on success
    """
    servo = maestro.Device()
    print('[SERVO] SERVO CONNECTION ESTABLISHED....')

    # 3 ESC, 5 STEERING

    servo.set_acceleration(cfg.STEERING, 50)
    servo.set_acceleration(cfg.ESC, 100)

    print('[SERVO] SENT SIGNAL....')
    servo.set_target(cfg.STEERING, cfg.MAX_RIGHT)
    time.sleep(1)
    servo.set_target(cfg.STEERING, cfg.MAX_LEFT)
    time.sleep(1)
    servo.set_target(cfg.STEERING, cfg.MAX_RIGHT)
    time.sleep(1)
    servo.set_target(cfg.STEERING, cfg.CENTER)
    print('[SERVO] STEERING ARMED....')
    time.sleep(1)

    servo.set_target(cfg.ESC, cfg.MAX_SPEED)
    servo.set_target(cfg.ESC, cfg.NEUTRAL)
    print('[SERVO] MOTOR ARMED....')
    time.sleep(1)

    print('[DEBUG] Exiting test_Device function')

    return 0


def servo_ctl(servo_num, val):
    """
    Function to send signal to Maestro servo Device for execution

    :param servo_num: <Int> 3 for speed, 5 for steering
    :param val: <Int> qms pulse value for the servo to execute
    :return: <Int> 0 on success
    """
    servo = maestro.Device()

    # TODO: Modify this to accommodate for speed
    servo.set_acceleration(cfg.STEERING, 50)
    servo.set_acceleration(cfg.ESC, 100)

    servo.set_target(servo_num, val)
    print('[DEBUG] Exiting servo_ctl function')

    return 0


def execute_data(data, conn):
    """
    Function to handle data processing and socket network disconnect

    :param data: <String> data to be processed
    :param conn: <Connection object> created after successful connect
    :return:    <Int> 404 if servo disconnects
                <Int> 0 on success
    """
    # data = data[2:len(data)-1]
    print("__" + data + "__")

    if data == 'kill':
        conn.close()
        print('[DEBUG] Terminating Client')
        sys.exit()
    elif data == 'start':
        conn.sendall(b'started')
        pass
    elif data == 'stop':
        print('[DEBUG] ***** Stopping')
        conn.sendall(b'stopped')
    elif data == 'gps':
        # conn.sendall(b'getting gps fix')
        get_gps(conn)
    elif data == 'disconnect':
        print('[NETWORK] Disconnect')
        conn.sendall(b'disconnecting')
        time.sleep(10)
        conn.close()
        return 404
    else:

        tgt = int(data[0])
        val = int(data[1:len(data)])

        print("target: " + str(tgt) + "\nvalue: " + str(val))

        # Guard statement to protect servossy
        if tgt == cfg.ESC and val > cfg.MAX_TEST_SPEED:
            print('[WARN] Speed would exceed testing limits!')
        else:
            if cfg.MAX_RIGHT <= val <= cfg.MAX_LEFT:
                print('[SERVO] Entering servo_ctl function with value of: ' +
                      str(val))

        conn.sendall(b'turn received')

    print('[DEBUG] Exiting execute_data function')

    return 0


def get_gps(conn):
    """
    Polls the GPS chip from the RPi3 and sends it to the server

    :param conn: <Connection object> Created by successful socket connection
    :return: <Int> 0 on success
    """
    message = "$GPGGA,172814.0,3723.46587704,N,12202.26957864,W,2,6,1.2,18.893, \
              M,-25.669,M,2.0,0031*4F"
    print('[GPS] ' + message)
    conn.sendall(message.encode('utf8'))
    print('[GPS] GPS SENT')
    print('[DEBUG] Exiting get_gps function')

    return 0


if __name__ == "__main__":
    main(port=int(sys.argv[1]))
