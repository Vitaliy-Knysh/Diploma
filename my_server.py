import socket

def connect():
    server = socket.socket()
    IP = socket.gethostbyname(socket.gethostname())
    PORT = 1034
    server.bind((IP, PORT))
    server.listen(1)
    usr, addr = server.accept()
    return usr, addr

def send(usr, char):
    usr.send(char.encode('utf-8'))

def listen(usr):
    try: data = usr.recv(1024).decode('utf-8')
    except socket.error:
        pass
    else: return data
