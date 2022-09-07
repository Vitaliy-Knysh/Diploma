import socket

command = 'l'
serverReadyFlag = False


def start():
    global serverReadyFlag
    global command
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP = socket.gethostbyname(socket.gethostname())
    PORT = 1034
    server.bind((IP, PORT))
    server.listen(1)
    usr, addr = server.accept()
    print('connected at ', usr)
    while True:
        data = usr.recv(400).decode('utf-8')
        print('data: ', data)
        if data:
            if data == 'r':
                print('ready flag received')
                usr.send(command.encode('utf-8'))
                print('command sent: ', command)
                command = 's'


def handle_client(usr):
    data = usr.recv(400).decode('utf-8')
    global serverReadyFlag
    if data: 
        if data == 'r' and serverReadyFlag == True:
            usr.send(command.encode('utf-8'))
            serverReadyFlag = False
    else: return 'n'

'''    while True:
        #if listen(usr) == 'r' and serverReadyFlag == True:
        send(usr, command)
        serverReadyFlag = False'''
