import socket
import thread
import fcntl
import struct
import json
import uuid


class ChatClient():

    def __init__(self):
        self.serverSoc = None
        self.serverStatus = 0
        self.buffsize = 1024
        self.allClients = {}
        self.ids = []
        self.counter = 0
        self.host_ip = (self.get_ip_address('wlan0'), 8090)

    def handleSetServer(self):
        if self.serverSoc is not None:
            self.serverSoc.close()
            self.serverSoc = None
            self.serverStatus = 0
        try:
            self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSoc.bind(self.host_ip)
            self.serverSoc.listen(5)
            print '\nServer listening on %s:%s' % self.host_ip
            thread.start_new_thread(self.listenClients, ())
            self.serverStatus = 1
            self.name = ''
            if self.name is '':
                self.name = "%s:%s" % self.host_ip
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
                chat_info = json.loads(clientsoc.recv(self.buffsize))
                id_rcv = chat_info['id']
                if not id_rcv in self.ids:
                    self.ids.append(id_rcv)
                    client = chat_info['from']
                    server = chat_info['to']
                    msg = chat_info['data']

                    if server == 'all':
                        print 'From: %s Message: %s' % (clientsoc.getpeername(), msg)

                    if server == self.host_ip[0]:
                        print '(Private) From: %s Message: %s' % (clientsoc.getpeername(), msg)
                    else:
                        for client in self.allClients.keys():
                            if client != clientsoc:
                                client.send(json.dumps(chat_info))
            except:
                break
        self.removeClient(clientsoc, clientaddr)
        clientsoc.close()
        print '\nClient disconnected from %s:%s' % clientaddr

    def handleSendChat(self, clientaddr=None):
        if self.serverStatus == 0:
            print '\nSet server address first'
            return

        msg = raw_input('Message: ')
        msg.join('\r\n')
        for client in self.allClients.keys():
            chat_info = {'from': self.host_ip[0], 'to': clientaddr,
                         'data': msg, 'id': str(uuid.uuid4())}
            client.send(json.dumps(chat_info))

    def addClient(self, clientsoc, clientaddr):
        self.allClients[clientsoc] = self.counter
        self.counter += 1

    def removeClient(self, clientsoc, clientaddr):
        print self.allClients
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
          '\tMensagem Privada: "@IP"\n'\
          '\tMensagem Publica: "all"\n'\
          '\tSair: Pressione Enter'
    while True:
        command = raw_input()
        if command is '':
            break
        if command[0] is '#':
            teste.handleAddClient((command[1:], 8090))
        if command[0] is '@':
            teste.handleSendChat(command[1:])
        if command == 'all':
            teste.handleSendChat('all')
