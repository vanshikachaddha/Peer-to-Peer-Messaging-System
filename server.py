import socket
import threading

HEADER = 64 
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) 
ADDR = (SERVER, PORT) 
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) #Bound the socket to address

#Runs for each client (running concurrently)
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    while connected:
        #First message tells us how long incoming message is
        msg_length = conn.recv(HEADER).decode(FORMAT) #Message is encoded in byte format
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
      
            conn.send("Msg recieved".encode(FORMAT))
    
    conn.close()

    

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        #Handle new connection
        conn, addr = server.accept() #Wait for new connection of the server (conn - communicate back)
        thread = threading.Thread(target = handle_client, args = (conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


print("[STARTING] server is starting")
start()

