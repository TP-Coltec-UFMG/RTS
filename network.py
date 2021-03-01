import socket
import pickle #Enables objects to be turned into byte information


class Network: #This class's purpose is to connect the client to the especified server
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "26.148.232.169" #Host IPV4 address
        self.port = 5555 #Port through wich server and client communicate
        self.addr = (self.server, self.port) #Address where the connection happens
        self.playerControls = self.connect()

    def getPlayerControl(self):
        return self.playerControls

    def connect(self):
        try:
            self.client.connect(self.addr)
            #Try connecting to the socket at the given address

            reply = self.client.recv(2048*16)
            return pickle.loads(reply)
            #Receives the byte data sent by the server in the form of a pickle object and loads it

        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            #Dumps "data" into a 'bytes' object and sends it to the server, in this case, an instance of a 'Control' object
            reply = self.client.recv(2048*64)
            return pickle.loads(reply)

        except socket.error as e:
            print(e)
