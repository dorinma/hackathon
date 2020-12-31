from socket import *
import struct
import time
import getch
import threading
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


msg_format = '!IBH'
cookie = 0xfeedbeef
msg_type = 0x2
clientPort = 13117
BUFFERSIZE = 1024
global game_on 
game_on = True
net = input("Please insert the number (2 for testing, any other character for playing)\n")
temp_host = get_if_addr('eth1') +'/16'
if net == '2':
    temp_host = get_if_addr('eth2') +'/16'
broadcast_host = str(ipaddress.ip_network(temp_host, False).broadcast_address)
print(bcolors.OKBLUE + bcolors.BOLD + "Client started," + bcolors.ENDC) 
print(bcolors.OKBLUE + "listening for offer requests..." + bcolors.ENDC)

def press_chars(sock):
    try:
        while True: #get char from the keyboard and send to server
            char = getch.getch() 
            if game_on:
                sock.send(char.encode())
            else:
                break
    except:
        pass

while True:
    #initialize variables
    serverIP = '0'
    msgPort = 0
    #UDP
    while True:
        try: 
            #waiting for a broadcast message from servers
            udpClient = socket(AF_INET, SOCK_DGRAM) 
            udpClient.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            udpClient.bind((broadcast_host, clientPort))
            data, addr = udpClient.recvfrom(BUFFERSIZE)
            (serverIP, serverPort) = addr
            (prefix, msgType, msgPort) = struct.unpack(msg_format, data) 
            if prefix != cookie or msgType != msg_type: #check if the message format isn't valid
                raise Exception
            print("Received offer from " + serverIP + ", attempting to connect...")
            time.sleep(0.1)
            break
        except:
            time.sleep(0.1)
            pass
    #TCP
    end_msg = ""
    try:
        tcpClient = socket(AF_INET, SOCK_STREAM) 
        tcpClient.connect((serverIP, msgPort)) #create a TCP connection to a server
        tcpClient.send("ISIS\n".encode()) #send the team name
        start_msg = tcpClient.recv(BUFFERSIZE).decode()
        print (start_msg)
        game_on = True
        game_thread = threading.Thread(target=press_chars, args=(tcpClient,)) #create the thread that runs the games
        game_thread.start() #start the game
        end_msg = tcpClient.recv(BUFFERSIZE).decode() #get end game message from server
        game_on = False
        game_thread.join()
        print(end_msg)
    except:
        pass
    print(bcolors.OKBLUE + "Server disconnected, listening for offer requests..." + bcolors.ENDC) #game over, starting again
