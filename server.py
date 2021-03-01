import socket
from _thread import *
import pickle
import pygame
pygame.init()
import classes
import copy

#global control
control = classes.Control()
conn = [0, 0]

def threaded_client(conn, playerId, otherPlayerId):
    #Creates new thread for the client that is connecting

    global control
    playerControls=[control, playerId]
    conn[playerId].send(pickle.dumps(playerControls))
    #Sends a list with the "control" object and the player ID to the client as soon as the connection is established

    reply = ""

    while True:
        if not isinstance(conn[otherPlayerId], int):
            try:
                data = pickle.loads(conn[otherPlayerId].recv(2048*64))
                control = copy.deepcopy(data[0])
                controlCopia = copy.deepcopy(data[1])

                if not data:
                    print("not data")
                    break
                    #If "data" doesn't receive anything, break, stoping the game
                elif control == controlCopia:
                    data[1] = False
                    conn[playerId].send(pickle.dumps(data))
                else:
                    data[1] = True
                    conn[playerId].send(pickle.dumps(data))
            except:
                break

    print("Lost connection")
    conn[0].close() #Closes the connection so the port may be reused
    conn[1].close()

def main():
    server = "26.148.232.169" #Host IPV4 address
    port = 5555 #Port through wich server and client communicate

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Place where communication happens, I guess

    try: #Try placing the socket at that port of that IP address
        s.bind((server, port))
    except socket.error as e:
        str(e)
    #If fails, returns error message

    s.listen(2)
    #Starts listening for (2 maximum) connections
    print("Waiting for a connection, Server Started")

    playerId = 0
    secondPlayerId = -1

    while True:
        conn[playerId], addr = s.accept()
        #As soon as the socket finds a connection that is trying to be established at its address, returns a new *socket* object to "conn" and the IP address that just connected with the socket to "addr"
        print("Connected to:", addr)
        print("playerId:", playerId)

        if playerId == 0:
            secondPlayerId = 1
        else:
            secondPlayerId = 0

        start_new_thread(threaded_client, (conn, playerId, secondPlayerId,))
        #Starts new thread of "threaded_client" with the arguments shown

        playerId = 1

if __name__ == "__main__":
    main()
