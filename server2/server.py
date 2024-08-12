import socket
import struct
import os

# Configurações iniciais:
from config import DEFAULT_IP, SERVER2_PORT, BUFFER_SIZE
    
def receive_file_size(sck: socket.socket):
    # This funcion makes sure that the bytes which indicate
    # the size of the file that will be sent are received.
    # The file is packed by the client via struct.pack(),
    # a function that generates a bytes sequence that
    # represents the file size.
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()
    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    filesize = struct.unpack(fmt, stream)[0]
    return filesize

def receive_file(sck: socket.socket, filename):
    filesize = receive_file_size(sck) # Pega a quantidade de bytes que serão recebidos
    # Abre um novo arquivo que armazenara os dados recebidos:
    with open(filename, "wb") as file:
        received_bytes = 0
        # Recebe o arquivo de data em pedaços de BUFFER_SIZE bytes até alcançar o tamanho do arquivo
        while received_bytes < filesize:
            chunk = sck.recv(BUFFER_SIZE)
            if chunk.endswith(b"<EOF>"):
                file.write(chunk[:-5])
                break
            file.write(chunk)
            received_bytes += len(chunk)


def send_file(sck: socket.socket, filename):
    filesize = os.path.getsize(filename) # Pega o tamanho do arquivo sendo enviado
    sck.sendall(struct.pack("<Q", filesize)) # Informa para o servidor a quantidade de bytes que será enviada
    # Envia o arquivo em chunks de BUFFER_SIZE-bytes
    with open(filename, "rb") as file:
        while chunk := file.read(BUFFER_SIZE):
            sck.sendall(chunk)
        sck.sendall(b"<EOF>")
        
def check_archive(filename):
    caminho = os.path.abspath(os.getcwd())
    for file in os.listdir(caminho):
        if(file == filename):
            return True
    return False

def send_increase_storage(conn, filename):
    if(check_archive(filename.decode())):
        filesize = os.path.getsize(filename) # Pego o tamanho do arquivo que eu tenho
        conn.send(str.encode(str(filesize))) # Aumento esse tamanho no server_dict
        conference = conn.recv(BUFFER_SIZE)
        print("Resposta:", conference.decode())
    else:
        conn.send(str.encode("False"))
        conference = conn.recv(BUFFER_SIZE)
        print("Resposta:", conference.decode())

TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) # Cria um socket TCP
TCPServerSocket.bind((DEFAULT_IP, SERVER2_PORT)) # Faz o bind de endereço IP e porta
TCPServerSocket.listen() # Ativa servidor para ficar ouvindo
print("SERVIDOR 2 ATIVADO!")

while True:
    print("Ouvindo...")
    conn, address = TCPServerSocket.accept() # Conexão aceita após solicitação do cliente/servidor
    print(f"Conexão Estabelecida: {address}")
    
    receiver = conn.recv(BUFFER_SIZE)
    print("Quem conectou é:", receiver.decode())
    conn.send(receiver)
    
    print("------------------RECEBENDO ARQUIVO----------------")
    filename = conn.recv(BUFFER_SIZE) # Recebo nome do arquivo do cliente/servidor
    print("Nome do arquivo recebido (CLIENT/SERVER):", filename.decode())
    conn.send(filename)
    
    # Faz a verificação se o arquivo já existe no servidor
    if(receiver.decode() == "client"):
        conn_manager, address = TCPServerSocket.accept() 
        print(f"Conexão Estabelecida com Manager: {address}")
        send_increase_storage(conn_manager, filename) # Se já tenho o arquivo, eu tenho que atualizar o armazenamento
    else:
        send_increase_storage(conn, filename) # Se já tenho o arquivo, eu tenho que atualizar o armazenamento
    # ---------------------- RECEBER ARQUIVO ----------------------------------
    print("Recebendo arquivo...")
    receive_file(conn, filename)
    print("Arquivo recebido!")
    
    # Encerro a conexão com quem se conectou
    conn.close()
    print("Conexão encerrada!")
    
    # Se for cliente, tenho que replicar
    if(receiver.decode() == "client"): 
        print("------------------FAZENDO REPLICAÇÃO - MANAGER----------------")
        data_replica = conn_manager.recv(BUFFER_SIZE) # Recebe DATA do MANAGER, contendo porta e token
        data_replica = data_replica.decode()
        
        if(data_replica != "Sem espaço para replicação"):
            dataSplit = data_replica.split('/')
            port = int(dataSplit[0])
            receiver = dataSplit[1]
            print("PORTA recebida do MANAGER:", port)
            print("------------------FAZENDO REPLICAÇÃO - SERVER----------------")    
            print(f"Conectando com o servidor {port}")
            TCPReplicaSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            TCPReplicaSocket.connect((DEFAULT_IP, port))
            print("Conexão com Servidor de Réplica Estabelecida!")
            # ----------------- ENVIAR RÉPLICA ----------------------------------
            print(f"Enviando token {receiver}")
            TCPReplicaSocket.send(str.encode(receiver))
            breaking = TCPReplicaSocket.recv(BUFFER_SIZE)
            print("(SERVER) RECEIVER recebido: ", breaking.decode())
    
            TCPReplicaSocket.send(filename) # Envia nome do arquivo enviado pelo cliente ao servidor de réplica
            uper = TCPReplicaSocket.recv(BUFFER_SIZE) # Recebe mensagem do servidor
            print("(SERVER) Nome do arquivo recebido:", uper.decode())
            
            # Servidor de réplica verifica se já tem o arquivo
            server_check = TCPReplicaSocket.recv(BUFFER_SIZE)
            server_check = server_check.decode()
            if(server_check != "False"): 
                TCPReplicaSocket.send(str.encode(f"Recebi o tamanho de arquivo existente: {server_check} bytes"))
            else:
                TCPReplicaSocket.send(str.encode("Recebi que o arquivo não existe."))   
            
            conn_manager.send(str.encode(server_check)) # Mando para o MANAGER se o arquivo já existe ou não no Servidor Réplica
            conference = conn_manager.recv(BUFFER_SIZE)
            print("MANAGER respondeu:", conference.decode())
    
            print("Enviando réplica...")
            send_file(TCPReplicaSocket, filename)
            print("Arquivo enviado!")
            
            # Conexão com servidor-réplica encerrada
            
            message = f"Arquivo enviado com sucesso para servidor {port}"
            conn_manager.send(str.encode(message))

        conn_manager.close() # Encerrar conexão SERVER-MANAGER
        print("Conexão encerrada com o MANAGER!")

    resp = input("Desligar servidor [S/N]? ")
    if (resp.lower() == "s"):
        break
    print()
    print("######################################")
    print()