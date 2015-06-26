import socket
import thread
import fcntl
import struct
import json

class ChatClient():

    def __init__(self):
        self.serverSoc = None
        self.serverStatus = 0
        self.buffsize = 1024
        self.allClients = {}
        self.counter = 0

    def handleSetServer(self):
        if self.serverSoc is not None:
            self.serverSoc.close()
            self.serverSoc = None
            self.serverStatus = 0
        serveraddr = (self.get_ip_address('wlan0'), 8090)
        #serveraddr = ('127.0.0.1', 8090)
        try:
            self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSoc.bind(serveraddr)
            self.serverSoc.listen(5)
            print '\nServer listening on %s:%s' % serveraddr
            thread.start_new_thread(self.listenClients, ())
            self.serverStatus = 1
            self.name = ''
            if self.name is '':
                self.name = "%s:%s" % serveraddr
        except:
            print '\nError setting up server'

    def listenClients(self):
        while 1:
            clientsoc, clientaddr = self.serverSoc.accept()
            print '\nClient connected from %s:%s' % clientaddr
            self.addClient(clientsoc, clientaddr)
            thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
        self.serverSoc.close()

    def handleAddClient(self, clientaddr):
        try:
            clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsoc.connect(clientaddr)
            print '\nConnected to client on %s:%s' % clientaddr
            self.addClient(clientsoc, clientaddr)
            thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
        except:
            print '\nError connecting to server'

    def handleClientMessages(self, clientsoc, clientaddr):
        while 1:
            try:
                data = clientsoc.recv(self.buffsize)
                #data = json.loads(clientsoc.recv(self.buffsize))
                #msg = data['data']
                #client = data['from']

                #if client is (self.get_ip_address('wlan0'), 8090):
                #    break
                #else:
                #for client in self.allClients.keys():
                #    #client.send(json.dumps(data))
                #    client.send(msg)

                print 'From: %s Message: %s' % (clientaddr, data)
                if not data:
                    break
                #self.addChat("%s:%s" % clientaddr, data)
            except:
                break
        self.removeClient(clientsoc, clientaddr)
        clientsoc.close()
        print '\nClient disconnected from %s:%s' % clientaddr

    def handleSendChat(self):
        if self.serverStatus == 0:
            print '\nSet server address first'
            return
        msg = raw_input('Menssagem: ')
        #data = {'from' : (self.get_ip_address('wlan0'), 8090), 'data' : msg}
        if msg == '':
            return
        #self.addChat("me", msg)
        for client in self.allClients.keys():
            #client.send(json.dumps(data))
            client.send(msg)
    #def addChat(self, client, msg):
        #self.receivedChats.config(state=NORMAL)
        #self.receivedChats.insert("end", client + ": " + msg + "\n")
        #self.receivedChats.config(state=DISABLED)

    def addClient(self, clientsoc, clientaddr):
        self.allClients[clientsoc] = self.counter
        self.counter += 1
        #self.friends.insert(self.counter, "%s:%s" % clientaddr)

    def removeClient(self, clientsoc, clientaddr):
        print self.allClients
        #self.friends.delete(self.allClients[clientsoc])
        del self.allClients[clientsoc]
        print self.allClients

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


if __name__ == '__main__':
    teste = ChatClient()
    teste.handleSetServer()
    print 'Comandos:\n'\
          '\tConectar-se: "#IP"\n'\
          '\tMensagem Publica: "all"\n'\
          '\tSair: Pressione Enter'
    while True:
        command = raw_input()
        if command is '':
            break
        if command[0] is '#':
            teste.handleAddClient((command[1:], 8090))
        if command == 'all':
            teste.handleSendChat()
