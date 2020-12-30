import threading
from socket import *
import time
import struct
import random
from scapy.all import get_if_addr
import ipaddress

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

max_score = 0
serverPort = 12000
myIP = get_if_addr('eth2') #gethostbyname(gethostname())
conns_map = {} #(connection, team name) map
keys = [] #connections list
g1_teams = [] 
g2_teams = []
g1_score = 0
g2_score = 0
lock1 = threading.Lock() #lock for the score counter variable of group 1
lock2 = threading.Lock() #same for group 2

#UDP server
def udp_server():
    print(bcolors.HEADER + bcolors.BOLD + "Server started," + bcolors.ENDC)
    print(bcolors.HEADER + "listening on IP address " + myIP + bcolors.ENDC)
    serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    serverSocket.bind(('', serverPort))
    broadcast = struct.pack('!IBH', 0xfeedbeef, 0x2, serverPort) #broadcast message
    serverSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    for i in range (0, 10):
        serverSocket.sendto(broadcast, ('172.99.255.255', 13117)) #send to everyone a broadcast message
        time.sleep(1)

def thread_per_client(conn, ip, port):
    try:
        while True:
            char = conn.recv(1) #the thread's client gets the input key from the client
            if g1_teams.__contains__(conn):
                lock1.acquire() #syncronizes the score counter variable for group 1
                global g1_score
                g1_score += 1
                lock1.release() #releases the score counter variable for group 1
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
    while time.time() < startGameTime: #runs this loop for 10 seconds
        try:
            tcpServer.listen(4) 
            (conn, (ip,port)) = tcpServer.accept() #waiting for clients to connect
            print("client on IP " + ip + " has connected")
            threads.append(threading.Thread(target= thread_per_client, args=(conn, ip, port,))) #creates thread for the current client
            team_name = conn.recv(1024) #get the client's team name
            conns_map[conn] = team_name.decode()
            keys.append(conn)
            time.sleep(0.1)
        except:
            pass
    try:
        random.shuffle(keys) #creates a random order for the clients and then divides them into 2 groups
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
        for conn in keys: #send the welcome msg to all the clients in the game
            conn.send(welcome_msg.encode())
        #starting the game: first run the clients' threads and then start the clock
        for t in threads:
            t.start()

        time.sleep(10) #game time
        #calculate the winning group
        winner = 0
        winners_names = ""
        end_msg = ""
        averagePerSecond = g1_score/10 #average keys per second for the winning team
        if g1_score > g2_score:
            winner = 1
            averagePerSecond = g1_score/10
        if g2_score > g1_score:
            winner = 2
            averagePerSecond = g2_score/10
        if winner == 1:
            winners_names = append_names(g1_teams)
        else:
            winners_names = append_names(g2_teams)
        global max_score
        if g1_score > max_score:
           # global max_score
            max_score = g1_score
        if g2_score > max_score:
            #global max_score
            max_score = g2_score
        #create the end game msg 
        if not winner == 0:
            end_msg = "Game over!\nGroup 1 typed in " + str(g1_score) + " characters.\nGroup 2 typed in " + str(g2_score) + " characters.\nGroup " + winner.__str__() + " wins!\nCongratulations to the winners:\n==\n" + winners_names
        else:
            end_msg = "Game over!\nGroup 1 typed in " + str(g1_score) + " characters.\nGroup 2 typed in " + str(g2_score) + " characters.\nIt's a tie! Thank you for playing :)\n"
        end_msg += "Max score so far -> " + str(max_score) + " keys!!!\n"
        end_msg += "Winning team's average keys per second -> " + str(averagePerSecond) + "!!!\n"
        if len(keys) > 0: #there were clients in the game
            print(end_msg) 

        for conn in keys: #sends to the clients the end msg
            conn.send(end_msg.encode())
            conn.close()
        #close TCP connections
        tcpServer.close()
        print(bcolors.HEADER + "Game over, sending out offer requests..." + bcolors.ENDC)
    except:
        #print (bcolors.FAIL + "Connection error" + bcolors.ENDC)
        time.sleep(0.1)
        pass

while True:
    #activate game threads
    tcpThread = threading.Thread(target=tcp_server, args=()) 
    udpThread = threading.Thread(target=udp_server, args=()) 
    tcpThread.start()
    udpThread.start()
    udpThread.join()
    tcpThread.join()
    #reset the variables for a new game
    serverPort = 12000
    myIP =  gethostbyname(gethostname()) 
    conns_map = {} #(connection, team name)
    g1_teams = []
    g2_teams = []
    keys = []
    g1_score = 0
    g2_score = 0
    lock1 = threading.Lock()
    lock2 = threading.Lock()
