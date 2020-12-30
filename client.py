from socket import *
import struct
import time
import getch
import threading

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

def press_chars(sock):
    try:
        while True: #get char from the keyboard and send to server
            char = getch.getch() 
            sock.send(char.encode())
    except:
        pass

print(bcolors.OKBLUE + bcolors.BOLD + "Client started," + bcolors.ENDC) 
print(bcolors.OKBLUE + "listening for offer requests..." + bcolors.ENDC)
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
            udpClient.bind(("", 13117))
            data, addr = udpClient.recvfrom(1024)
            (serverIP, serverPort) = addr
            (prefix, msgType, msgPort) = struct.unpack('IBH', data) 
            if prefix != 0xfeedbeef or msgType != 2: #check if the message format isn't valid
                raise Exception
            print("Received offer from " + serverIP + ", attempting to connect...")
            break
        except:
            #print(bcolors.FAIL + "Error occured" + bcolors.ENDC)
            pass
    #TCP
    end_msg = ""
    try:
        tcpClient = socket(AF_INET, SOCK_STREAM) 
        tcpClient.connect((serverIP, msgPort)) #create a TCP connection to a server
        tcpClient.send("ISIS\n".encode()) #send the team name
        start_msg = tcpClient.recv(1024).decode()
        print (start_msg)
        game_thread = threading.Thread(target=press_chars, args=(tcpClient,)) #create the thread that runs the games
        game_thread.start() #start the game
        end_msg = tcpClient.recv(1024).decode() #get end game message from server
        game_thread.join()
        print(end_msg)
    except:
        pass
    print(bcolors.OKBLUE + "Server disconnected, listening for offer requests..." + bcolors.ENDC) #game over, starting again
