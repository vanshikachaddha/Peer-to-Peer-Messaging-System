import socket
import threading

HEADER = 64 
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname()) 
ADDR = (SERVER, PORT)
username = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def start():
    global username
    print("Please input your username: ")
    username = input()
    while (not username):
        print("Please input your username: ")
        username = input()
    send(username)


def send(msg):

    message = msg.encode(FORMAT) #Encode string into byte like object
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) #Pad to make 64 bytes
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def recieve():
    while True:
        try:
            message = client.recv(2048).decode(FORMAT)
            print(message)
        except:
            pass

recieve_thread = threading.Thread(target=recieve)
recieve_thread.start()

start()

while True:
    message = input()
    send(message)
    if message == DISCONNECT_MESSAGE:
        break



