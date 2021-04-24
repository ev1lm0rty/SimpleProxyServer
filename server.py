import socket, sys, os
from _thread import *
from sys import argv
import json
import base64



# This Block of code receives the port number entered
# by the user at the terminal

try:
    this_port = argv[1]
    # this_port = input("[*] Enter the listening port: ")
    listening_port = int(os.environ.get("PORT", this_port))
except KeyboardInterrupt:
    print("\n[*] User has requested an interrupt")
    print("[*] Application Exiting.....")
    sys.exit()

# Maximum connections queues
max_conn = 20
# Maximum socket's buffer size
buffer_size = 8192000
level=0

# This function starts binding the socket to ports
# This function ensure only authorize user can start the server
# This function waits for client request
# When a request is received it starts a new thread to manage the request
def start():  # Main Program
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initializing the socket
        s.bind(('', listening_port))  # Binding the socket to listen at the port
        s.listen(max_conn)  # Start listening for connections
        print("[*] Initializing sockets........ Done!")
        print("[*] Sockets bound successfully......")
        print("[*] Server started successfully [ %d ]\n" % (listening_port))
        go=0
        while 1:
            name = input("Username:")
            password = input("Password:")
            if (authorize(name, password) == -1):
                print("Invalid Username/Password!!!")
                go=go+1
                if go>2:
                    print("Maximum Attempt Reached!!!")
                    sys.exit(1)
            else:
                print("Authorized Successfully!!")
                print("Proxy Server Started!!")
                break



    except Exception:  # Will be executed if anything fails
        print("[*] Unable to Initialize Socket")
        sys.exit(2)

    while 1:
        try:
            conn, addr = s.accept()  # Accept connection from client browser
            data = conn.recv(buffer_size)  # Recieve client data
            start_new_thread(conn_string, (conn, data, addr))  # Starting a thread
            # conn_string(conn,data,addr)
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Proxy server shutting down....")
            print("[*] Have a nice day... ")
            sys.exit(1)
    s.close()


# This function checks whether user is authorized or not
# It extracts the domain from the user request
# check for blacklist and blacklist bypass
# further it sends request to proxyserver to get the request processed
def conn_string(conn, data, addr):
    try:
        global level
        flag = 0
        data = data.decode('utf-8')
        if autho(data) == -1:
            print("Unauthorized")
            level=0
        else:
            flag = 1

        print("")
        first_line = data.split('\n')[0]
        url = first_line.split(' ')[1]
        http_pos = url.find("://")  # Finding the position of ://
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]
        port_pos = temp.find(":")

        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if (port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        if blacklist(webserver) or level==1:
            proxy_server(webserver, port, conn, addr, data)
        else:
            print("[!] Not allowed")
            conn.close()
            sys.exit()
    except Exception:
        pass


# This function sends request to url given by user
# Then the reply from the url request is given back to client
def proxy_server(webserver, port, conn, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(bytes(data, 'utf-8'))

        while 1:
            reply = s.recv(100000)
            if (len(reply) > 0):
                conn.send(reply)
                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print("[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar)))
                print()
                print()
            else:
                break

        s.close()
        conn.close()
    except:
        s.close()
        conn.close()
        sys.exit(1)


# This function checks whether domain is present in the blacklist
# and accordingly sends the response
def blacklist(domain):
    blacklist_file = 'blacklist.txt'
    f = open(blacklist_file, 'r')
    lines = f.readlines()
    f.close()
    for i in lines:
        if domain in i.strip():
            return False
    return True


# This function checks whether username and password given by user is correct or not
def authorize(name, password):
    with open('auth.json', 'r') as file:
        obj = json.load(file)
    if name in obj:
        if password == obj[name][0]:
            return obj[name][1]
        else:
            return -1
    else:
        return -1


# This function extracts username and password from the curl request
def autho(s):
    lines = s.split('\n')
    for i in lines:
        if "Authorization" in i:
            s = i.split(" ")[2]
            b = s.encode('ascii')
            mb = base64.b64decode(b)
            mmm = mb.decode('ascii')
            user = mmm.split(':')
            print("User:" + user[0])
            global level
            coin = authorize(user[0], user[1])
            level=coin
            return coin
    return -1


start()
