import os
import socket
import sys
import time

import global_cfg as cfg
import maestro as maestro


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', cfg.PORT))
    except socket.error as emsg1:
        print(emsg1)
        sys.exit()

    sock.listen(5)

    print('[NETWORK] SERVER ESTABLISHED....')

    # test_controller('/dev/ttyACM0')

    print('[SERVO] TESTING COMPLETE....')
    print('[NETWORK] IP: ' + str(cfg.CLIENT_IP_A) + ' PORT: ' + str(cfg.PORT))
    while True:
        (conn, address) = sock.accept()
        try:
            while True:
                try:
                    data = conn.recv(64)
                    if data:
                        print('[DEBUG] Recieved data from: ' + conn.getpeername().__str__() + '\t\t' + data.__str__())
                        # result = test_run(data, conn)

                        # if result == 404:
                        # break

                except TypeError as emsg2:
                    print('[WARN] ' + str(emsg2))
                    conn.close()
                    sys.exit()
                except socket.error:
                    print('[WARN][NETWORK] Socket error')
                    break
        except KeyboardInterrupt:
            test_run('stop', conn)



def test_controller(port):
    servo = maestro.Controller(port)
    print('[SERVO] SERVO CONNECTION ESTABLISHED....')

    # 3 ESC, 5 STEERING

    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)
    print(servo.getMin(cfg.STEERING), servo.getMax(cfg.STEERING))

    print('[SERVO] SENT SIGNAL....')

    servo.setTarget(cfg.STEERING, cfg.MAX_RIGHT)
    print(servo.getPosition(cfg.STEERING))
    time.sleep(1)
    servo.setTarget(cfg.STEERING, cfg.MAX_LEFT)
    print(servo.getPosition(cfg.STEERING))
    time.sleep(1)
    servo.setTarget(cfg.STEERING, cfg.MAX_RIGHT)
    print(servo.getPosition(cfg.STEERING))
    time.sleep(1)
    servo.setTarget(cfg.STEERING, cfg.CENTER)
    print('[SERVO] STEERING ARMED....')
    time.sleep(1)

    print(servo.getPosition(cfg.ESC))
    servo.setTarget(cfg.ESC, 8000)
    servo.setTarget(cfg.ESC, cfg.NEUTRAL)
    print(servo.getPosition(cfg.ESC))
    print('[SERVO] MOTOR ARMED....')
    time.sleep(1)

    print('[DEBUG] Exiting test_controller function')


def servo_ctl(servo_num, val):
    servo = maestro.Controller('/dev/ttyACM0')

    # TODO: Modify this to accommodate for speed
    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)

    servo.setTarget(servo_num, val)
    print('[DEBUG] Exiting servo_ctl function')

def test_run(arg, conn):
    # arg = arg[2:len(arg)-1]
    print(arg)

    if arg == 'kill':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        conn.close()
        print('[DEBUG] Terminating Client')
        sys.exit()
    elif arg == 'start':
        servo_ctl(cfg.STEERING, cfg.MAX_RIGHT)
        servo_ctl(cfg.ESC, cfg.TEST_SPEED)
    elif arg == 'stop':
        print('[DEBUG] ***** Stopping')
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
    elif arg == 'gps':
        get_gps(conn)
    elif arg == 'disconnect':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        print('[NETWORK] Disconnect')
        time.sleep(10)
        conn.close()
        return 404
    else:

        tgt = int(arg[0])
        val = int(arg[1:len(arg)])

        # Guard statement to protect servossy
        if tgt == cfg.ESC and val > cfg.MAX_TEST_SPEED:
            print('[WARN] Speed would exceed testing limits!')
        else:
            if 4000 <= val <= 8000:
                print('[SERVO] Entering servo_ctl function with value of: ' + str(val))
                servo_ctl(tgt, val)

    print('[DEBUG] Exiting test_run function')

def get_gps(conn):
    os.system('grep --line-buffered -m 1 GGA /dev/ttyACM2 > gps.txt')
    myfile = open('gps.txt', 'r')
    message = myfile.read()
    myfile.close()
    print('[GPS] ' + message)
    conn.sendall(message.encode())
    print('[GPS] GPS SENT')
    print('[DEBUG] Exiting get_gps function')



if __name__ == "__main__":
    main()
