import socket
import threading

HEADER = 64 
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) 
ADDR = (SERVER, PORT) 
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
clients = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) #Bound the socket to address

#Runs for each client (running concurrently)
# Conn = connection to client and Addr = address of client (identify which client you're talking to)
def recieve_message(conn, addr):
    connected = True
    username = None

    while connected:
        #First message tells us how long incoming message is
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT) #Message is encoded in byte format
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    del clients[addr]
                
                if username is None:
                    username = msg
                    clients[addr] = (conn, username)
                    print(f"[NEW CONNECTION] {username} connected.")
                    continue

                print(f"[{clients[addr][1]}] {msg}")

                
                for client_addr, (client_conn, name) in clients.items():
                    if client_addr != addr:
                        client_conn.send(f"[{name}] {msg}".encode(FORMAT))
        except:
            connected = False
                    
    
    conn.close()

    

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        #Handle new connection
        conn, addr = server.accept() #Wait for new connection of the server (conn - communicate back)
        thread = threading.Thread(target = recieve_message, args = (conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


print("[STARTING] server is starting")
start()

