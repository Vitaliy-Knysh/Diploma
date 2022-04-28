from jetbot import Robot
import socket
import time

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


def send(msg):
    message = msg.encode(FORMAT)
    client.send(message)
    
    
send('r')
while True:
    data = client.recv(20).decode(FORMAT)
    if data:
        if data == 'f':
            leftMotor = rightMotor = 0.5
            moveTime = 0.5
        elif data == 'l':
            leftMotor = 0
            rightMotor = 0.5
            moveTime = 0.15
        elif data == 'r':
            leftMotor = 0.5
            rightMotor = 0
            moveTime = 0.15
        elif data == 's':
            leftMotor = 0
            rightMotor = 0
            moveTime = 1
        robot.set_motors(leftMotor, rightMotor)
        time.sleep(moveTime)
        robot.set_motors(0, 0)
        print(data)
        send('r')
        if data == 'c':
            conn.close()
            break
