import socket
import thread
import fcntl
import struct
import json
import uuid


class P2P():

    def __init__(self):
        # Socket servidor
        self.serverSoc = None

        # Tamanho do Buffer
        self.buffsize = 1024

        # Dicionario contendo todos os clientes conectados
        self.allClients = {}

        # Lista de ids de mensagens
        self.ids = []

        # Contador utilizado no dicionario para a quantidade
        self.counter = 0

        # IP de interface de rede
        self.host_ip = (self.get_ip_address('wlan0'), 8090)

    # Seta o servidor
    def setServer(self):

        # Verifica se o server esta ativo e realiza o desativamento
        if self.serverSoc is not None:
            self.serverSoc.close()
            self.serverSoc = None
            self.serverStatus = 0
        try:
            # Cria socket do server com o IP e porta padrao
            self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSoc.bind(self.host_ip)
            self.serverSoc.listen(5)
            print '\nServidor ouvindo em %s:%s' % self.host_ip

            # Com o server setado comecamos a ouvir conexoes de outros peers
            thread.start_new_thread(self.listenClients, ())
            self.name = ''
            if self.name is '':
                self.name = "%s:%s" % self.host_ip
        except:
            print '\nErro em inicializar o servidor'

    # Metodo que que ouve a porta para a conexao de clientes
    def listenClients(self):
        while 1:
            # Aceita a conexao
            clientsoc, clientaddr = self.serverSoc.accept()
            print '\nNovo cliente conectado (%s:%s)' % clientaddr

            # Adiciona o socket client no dicionario de peers conectados
            self.addClient(clientsoc, clientaddr)

            # Inicializa a thread que ouve o que cliente escreve e manda para pos peers conectados
            thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
        self.serverSoc.close()

    # Cria o socket do novo peer e comeca a ouvir mensagens vindas do mesmo
    def handleAddClient(self, clientaddr):
        try:
            # Cria socket o novo peers
            clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsoc.connect(clientaddr)
            print '\nConectado ao cliente (%s:%s)' % clientaddr

            # Adiciona o socket client no dicionario de peers conectados
            self.addClient(clientsoc, clientaddr)

            # Inicializa a thread que ouve menssagens enviadas por este novo peer
            thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
        except:
            print '\nErro ao conectar com o servidor'

    # Thread que fica ouvindo menssagens recebidas do socket do peers conectado
    def handleClientMessages(self, clientsoc, clientaddr):
        while 1:
            try:
                # Recebe JSON vindo de um peer conectado
                chat_info = json.loads(clientsoc.recv(self.buffsize))
                id_rcv = chat_info['id']

                # Checa se a mensagem ja foi recebida
                if not id_rcv in self.ids:
                    # Se nao foi, adiciona ela as mensagens recebidas
                    self.ids.append(id_rcv)
                    client = chat_info['from']
                    server = chat_info['to']
                    msg = chat_info['data']

                    # Verifica se a menssagem recebida eh global
                    if server == 'all':
                        print '%s: %s' % (clientsoc.getpeername(), msg)

                    # Verifica se a menssagem recebida e privada
                    if server == self.host_ip[0]:
                        print '(Privado) %s: %s' % (clientsoc.getpeername(), msg)

                    # Se nao for privada
                    else:
                        # Replica a menssagem para todos os peers conectados
                        # (menos o que enviou)
                        for client in self.allClients.keys():
                            if client != clientsoc:
                                client.send(json.dumps(chat_info))
            except:
                break
        self.removeClient(clientsoc, clientaddr)
        clientsoc.close()
        print '\nCliente desconectado (%s:%s)' % clientaddr

    def handleSendChat(self, clientaddr=None, text=None):
        if text is None:
            text = raw_input()
        msg = text
        for client in self.allClients.keys():
            chat_info = {'from': self.host_ip[0], 'to': clientaddr,
                         'data': msg, 'id': str(uuid.uuid4())}
            client.send(json.dumps(chat_info))

    # Adiciona peer ao dicionario de peers conectados
    def addClient(self, clientsoc, clientaddr):
        self.allClients[clientsoc] = self.counter
        self.counter += 1

    # Remove peer do dicionario de peers conectados
    def removeClient(self, clientsoc, clientaddr):
        print self.allClients
        del self.allClients[clientsoc]
        print self.allClients

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


if __name__ == '__main__':
    chat = P2P()
    chat.setServer()
    print 'Comandos:\n'\
          '\tConectar: "#IP"\n'\
          '\tMenssagem Privada: "@IP", pressione Enter e digite a mensagem\n'\
          '\tSair: "q"'
    while True:
        command = raw_input()
        if command[0] is 'q':
            break
        if command[0] is '#':
            chat.handleAddClient((command[1:], 8090))
        if command[0] is '@':
            chat.handleSendChat(command[1:])
        else:
            chat.handleSendChat('all', command)
