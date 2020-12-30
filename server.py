import threading
from socket import *
import time
import struct
import random

serverPort = 12000
myIP = gethostbyname(gethostname())
conns_map = {} #(connection, team name)
g1_teams = []
g2_teams = []
g1_score = 0
g2_score = 0
lock1 = threading.Lock() #lock for the list of group 1
lock2 = threading.Lock() #lock for the list of group 2
stop_threads = False 

#UDP server
def udp_server():c
    print("Server started, listening on IP address " + myIP)
    serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    serverSocket.bind(('', serverPort))
    broadcast = struct.pack('!IBH', 0xfeedbeef, 0x2, 13117) 
    print (broadcast)
    serverSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    for i in range (0, 10):
        serverSocket.sendto(broadcast, ('<broadcast>', 13117))
        time.sleep(1)

def thread_per_client(conn, ip, port):
    try:
        while True:
            char = conn.recv(1)
            if g1_teams.__contains__(conn):
                lock1.acquire()  
                global g1_score
                g1_score += 1
                lock1.release()
            if g2_teams.__contains__(conn):
                lock2.acquire()  
                global g2_score
                g2_score += 1
                lock2.release()
    except:
        pass

#catenate list of teams' names to a string
def append_names(lst):
    msg = ""
    for l in lst:
        msg += conns_map[l] + "\n"
    return msg

#TCP server
def tcp_server():
    tcpServer = socket(AF_INET, SOCK_STREAM) 
    tcpServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 
    tcpServer.bind((myIP, serverPort)) 
    threads = []
    startGameTime = time.time() + 10
    tcpServer.settimeout(3)
    while time.time() < startGameTime:
        try:
            tcpServer.listen(4) 
            (conn, (ip,port)) = tcpServer.accept() 
            print(ip +" - client connected")
            threads.append(threading.Thread(target= thread_per_client, args=(conn, ip, port,)))
            team_name = conn.recv(1024)
            conns_map[conn] = team_name.decode()
        except:
            pass
    keys = conns_map.keys()
    random.shuffle(keys)
    i = 0
    for k in keys:
        if i == 0:
            g1_teams.append(k)
            i = 1
        else:
            g2_teams.append(k)
            i = 0
    welcome_msg = "Welcome to Keyboard Spamming Battle\nGroup 1:\n==\n" + append_names(g1_teams)
    welcome_msg += "Group 2:\n==\n" + append_names(g2_teams)
    welcome_msg += "Start pressing keys on your keyboard as fast as you can!"
    for conn in keys:
        conn.send(welcome_msg.encode())
    #starting the game: first run the clients' threads and then start the clock
    for t in threads:
        t.start()

    #endGameTime = time.time() + 10
    time.sleep(10)
    winner = 0
    winners_names = ""
    end_msg = ""
    if g1_score > g2_score:
        winner = 1
    if g2_score > g1_score:
        winner = 2
    if winner == 1:
        winners_names = append_names(g1_teams)
    else:
        winners_names = append_names(g2_teams)
    if not winner == 0:
        end_msg = "Game over!\nGroup 1 typed in " + str(g1_score) + " characters.\nGroup 2 typed in " + str(g2_score) + " characters.\nGroup " + winner.__str__() + " wins!\nCongratulations to the winners:\n==\n" + winners_names
    else:
        end_msg = "Game over!\nGroup 1 typed in " + str(g1_score) + " characters.\nGroup 2 typed in " + str(g2_score) + " characters.\nIt's a tie! Thank you for playing :)\n"
    print(end_msg)

    for conn in keys:
        conn.send(end_msg.encode())
        conn.close()
    #close TCP connections
    tcpServer.close()
    print("Game over, sending out offer requests...")

while True:
    tcpThread = threading.Thread(target=tcp_server, args=()) 
    udpThread = threading.Thread(target=udp_server, args=()) 
    tcpThread.start()
    udpThread.start()
    udpThread.join()
    tcpThread.join()
    serverPort = 12000
    myIP =  gethostbyname(gethostname()) 
    conns_map = {} #(connection, team name)
    g1_teams = []
    g2_teams = []
    g1_score = 0
    g2_score = 0
    lock1 = threading.Lock()
    lock2 = threading.Lock()
