from socket import *
import struct
import time
import getch
import threading

#host = '127.0.1.1' #41

def press_chars(sock):
    try:
        while True:
            char = getch.getch()
            sock.send(char.encode())
    except:
        pass

print("Client started, listening for offer requests...")
while True:
    serverIP = '0'
    msgPort = 0
    #UDP
    while True:
        try:
            udpClient = socket(AF_INET, SOCK_DGRAM) 
            udpClient.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            udpClient.bind(("", 13117))
            data, addr = udpClient.recvfrom(1024)
            (serverIP, serverPort) = addr
            serverIP = '172.1.0.89' #just for testing
            # (prefix, msgType, msgPort) = struct.unpack('IBH', data)
            # if prefix != 0xfeedbeef or msgType != 2:
            #     raise Exception
            #msgPort = struct.unpack('>H', data[5:7])[0]
            msgPort = 12000 #just for testing
            print("Received offer from " + serverIP + ", attempting to connect...")
            break
        except:# expression as identifier:
            #print(identifier)
            print("Failed to connect to server, trying again...")
            pass
    #TCP
    try:
        tcpClient = socket(AF_INET, SOCK_STREAM) 
        print(serverPort)
        tcpClient.connect((serverIP, serverPort))
        print("connected")
        tcpClient.send("ISIS\n".encode())     
        start_msg = tcpClient.recv(1024).decode()
        print (start_msg)
        game_thread = threading.Thread(target=press_chars, args=(tcpClient,)) #create the thread that runs the games
        game_thread.start() #start the game
        end_msg = tcpClient.recv(1024).decode()
        game_thread.join()
    except:
        end_msg = "receive err"
    print(end_msg)
    #tcpClient.close()
    print("Server disconnected, listening for offer requests...") #game over, starting again


#tcpClient.close() 
