from jetbot import Robot
import socket
import time
from rplidar import RPLidar

lidar = RPLidar('/dev/ttyUSB0')
arr = []
leftMotor = rightMotor = moveTime = 0
PORT = 1034
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.0.187"
ADDR = (SERVER, PORT)
robot = Robot()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print('connected')
lidar.start_motor()


def send(msg):
    message = msg.encode(FORMAT)
    client.send(message)
    
    
send('r')
while True:
    data = ''
    data = client.recv(20).decode(FORMAT)
    if data:
        if data == 'f':
            leftMotor = rightMotor = -0.5
            moveTime = 0.15
        elif data == 'l':
            leftMotor = 0
            rightMotor = -0.5
            moveTime = 0.15
        elif data == 'r':
            leftMotor = -0.5
            rightMotor = 0
            moveTime = 0.15
        elif data == 's':
            leftMotor = 0
            rightMotor = 0
            moveTime = 1
        elif data == 'm':  # получение данных с лидара
            lidar.start_motor()
            data = ''
            robot.set_motors(0, 0)
            time.sleep(1)
            leftMotor = 0
            rightMotor = 0
            moveTime = 0
            for i, scan in enumerate(lidar.iter_scans(scan_type='express')):
                print('%d: Got %d measurments' % (i, len(scan)))
                if len(scan) > 100:
                    arr = scan
                    break
                if i >= 2:
                    break
            for i in arr:
                data += str(round(i[1], 1)) + ' ' + str(round(i[2])) + ' '
            send(data)
            lidar.stop()

            
        robot.set_motors(leftMotor, rightMotor)
        time.sleep(moveTime)
        robot.set_motors(0, 0)
        time.sleep(0.3)
        print(data)
        send('r')
        if data == 'c':
            conn.close()
            break
