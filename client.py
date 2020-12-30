from socket import *
import struct
import time
import getch
import threading

def press_chars(sock):
    try:
        while True:
            char = getch.getch()
            sock.send(char.encode())   
    except:
        pass
#UDP
print("Client started, listening for offer requests...")
while True:
    udpClient = socket(AF_INET, SOCK_DGRAM) 
    udpClient.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    udpClient.bind(("", 13117))
    data, addr = udpClient.recvfrom(2048)
    (serverIP, serverPort) = addr
    (prefix, msgType, port) = struct.unpack('I B H', data)
    print("Received offer from " + serverIP + ", attempting to connect...")
    #TCP
    tcpClient = socket(AF_INET, SOCK_STREAM) 
    tcpClient.connect(('127.0.1.1', port))
    print("connected")
    tcpClient.send("ISIS\n".encode())     
    msg = tcpClient.recv(1024).decode()
    print (msg)
    game_thread = threading.Thread(target=press_chars, args=(tcpClient,)) #create the thread that runs the games
    game_thread.start() #start the game
    # end_game = time.time() + 10
    # while time.time() < end_game or game_thread.is_alive:
    #     time.sleep(0.1)
    # time.sleep(10)
    # if game_thread.is_alive(): #if the thread is blocked, waiting for io 
    #     game_thread._tstate_lock()
    #     game_thread._stop()
    #     game_thread.kill()
    game_thread.join()
    tcpClient.close()
    print("Server disconnected, listening for offer requests...") #game over, starting again


#tcpClient.close() 