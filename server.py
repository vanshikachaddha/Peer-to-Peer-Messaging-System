import socket
import threading

HEADER = 64 
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) 
ADDR = (SERVER, PORT) 
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
clients = {}
clients_by_name = {}
pending_dms = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) #Bound the socket to address

#Runs for each client (running concurrently)
# Conn = connection to client and Addr = address of client (identify which client you're talking to)
def recieve_message(conn, addr):
    connected = True
    username = None
    dm_mode = False
    dm_target = None

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
                    clients_by_name[username] = conn
                    print(f"[NEW CONNECTION] {username} connected.")
                    continue

                if (msg == "/list"):
                    user_list = []
                    for _, (_, users) in clients.items():
                        if (users != username):
                            user_list.append(users)
                        
                    conn.send(f"[SERVER] Online users: {user_list}".encode(FORMAT))
                    continue

                # User wanting to DM another user
                if (msg == "/dm"):
                    dm_mode = True
                    user_list = []
                    for _, (_, users) in clients.items():
                        if (users != username):
                            user_list.append(users)
                    conn.send(f"[SERVER] Online users: {user_list} \nWho would you like to text?".encode(FORMAT))
                    continue

                # Picking who to DM
                if (dm_target == None and dm_mode):
                    if (msg in clients_by_name):
                        dm_target = msg
                        pending_dms[dm_target] = username
                        conn.send(f"[SERVER] Waiting for {dm_target}'s response".encode(FORMAT))
                        client_conn = clients_by_name[dm_target]
                        client_conn.send(f"{username} wants to dm you. Type /accept {username} to continue".encode(FORMAT))
                    else:
                        dm_mode = False
                        conn.send(f"[SERVER] {msg} does not exist.".encode(FORMAT))
                    continue

                # User accepting DM invitation
                if (msg.startswith("/accept") and pending_dms[username] == msg.split()[1].strip()):
                    del pending_dms[username]
                    dm_mode = True
                    dm_target = msg.split("/accept ", 1)[1].strip()
                    conn.send(f"[SERVER] You're now in a private chat with {dm_target}. Type /exit to return to the group.".encode(FORMAT))
                    client_conn = clients_by_name[dm_target]
                    client_conn.send(f"[SERVER] You're now in a private chat with {username}. Type /exit to return to the group.".encode(FORMAT))
                    continue

                if (msg == "/exit"):
                    client_conn = clients_by_name[dm_target]
                    client_conn.send(f"[SERVER] {username} exited the private chat. Type /exit to return to the group.".encode(FORMAT))
                    dm_mode = False
                    dm_target = None
                    continue
                
     
                print(f"[{clients[addr][1]}] {msg}")

                if (dm_mode == False):
                    for client_addr, (client_conn, name) in clients.items():
                        if client_addr != addr:
                            client_conn.send(f"[{clients[addr][1]}] {msg}".encode(FORMAT))
                elif (dm_mode == True):
                    for _, (client_conn, name) in clients.items():
                        if (name == dm_target):
                            client_conn.send(f"[{clients[addr][1]}] {msg}".encode(FORMAT))

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

