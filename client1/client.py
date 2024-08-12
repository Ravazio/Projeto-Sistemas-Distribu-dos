import socket
import struct
import os

# Configurações iniciais:
from config import DEFAULT_IP, MANAGER_PORT, BUFFER_SIZE

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

TCPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) # Cria um socket TCP
TCPClientSocket.connect((DEFAULT_IP, MANAGER_PORT)) # Solicita conexão ao manager

# Conexão aceita:
while True:
    #print("Cliente conectado com Manager!")
    filename = input("Digite o nome do arquivo que deseja enviar: ")
    
    if(check_archive(filename)):
        filesize = os.path.getsize(filename)
        TCPClientSocket.send(str.encode(str(filesize)))
        
        # Recebe data do manager contendo a porta do servidor a se conectar e a chave de conexão:
        data = TCPClientSocket.recv(BUFFER_SIZE)
        data = data.decode()
        if(data != "Espaço Insuficiente"):    
            dataSplit = data.split('/')
            port = int(dataSplit[0])
            receiver = dataSplit[1]
            
            #print(f"Conectando com servidor {port}")
            TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            TCPServerSocket.connect((DEFAULT_IP, port))
            print("Conectado com servidor!")
            
            TCPServerSocket.send(str.encode(receiver))
            breaking = TCPServerSocket.recv(BUFFER_SIZE)
            #print("(SERVER) RECEIVER recebido: ", breaking.decode())
        
            TCPServerSocket.send(str.encode(filename)) # Envia para o servidor o Filename
            
            #print("------------------RESPOSTA DO SERVIDOR----------------")
            response = TCPServerSocket.recv(BUFFER_SIZE) # Recebe mensagem do servidor
            #print("(SERVER) Nome do arquivo recebido:", response.decode())
            
            TCPClientSocket.send(str.encode("Verifique com o SERVER se ele já tem o arquivo"))
        
            # ---------------------- ENVIAR ARQUIVO ----------------------------------
            print("Enviando arquivo...")
            send_file(TCPServerSocket, filename)
            print("Arquivo enviado!")
            
            # Conexão com servidor encerrada
        
            message = f"Arquivo enviado com sucesso para servidor {port}"
            TCPClientSocket.send(str.encode(message))
        else:
            print(data)
    else:
        TCPClientSocket.send(str.encode("Arquivo não encontrado!"))
        response = TCPClientSocket.recv(BUFFER_SIZE)
        print(response.decode())

    resp = input("Deseja parar de enviar arquivos [S/N]? ")
    TCPClientSocket.send(str.encode(resp))
    if (resp.lower() == "s"):
        break
    print()
    print("###########################################################")
    print()