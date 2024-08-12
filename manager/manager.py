import socket

# Configurações iniciais:
from config import DEFAULT_IP, MANAGER_PORT, BUFFER_SIZE, server_dict

def print_dict(server_dict):
    for port, capacity in server_dict.items():
        print(f"Porta: {port} | Tamanho: {capacity} bytes")

# Algoritmo de seleção das portas dos servidores a serem enviados
def select_ports(server_dict, filesize):
    print("SERVIDORES:")
    print_dict(server_dict)
    
    # Ordernar server_dict com base nos valores (capacidade armazenamento):
    tuple_sorted_servers = sorted(server_dict.items(), key=lambda item: item[1], reverse=True)     
    server_dict = dict(tuple_sorted_servers)
    
    print("SERVIDORES ORDENADOS:")
    print_dict(server_dict)

    # Selecionar 2 primeiras portas:
    mainServer_port = tuple_sorted_servers[0][0]
    copyServer_port = tuple_sorted_servers[1][0]
    print(f"Servidor Principal: {mainServer_port} | Servidor Secundário: {copyServer_port}")
    
    valid_token = 0
    if(server_dict[mainServer_port] < filesize):
        print("Espaço insuficiente nos servidores. Não é possível transferir arquivo.")
        valid_token = 1
    elif(server_dict[copyServer_port] < filesize):
        print("Espaço insuficiente para réplica. Não é possível replicar arquivo.")
        valid_token = 2
    
    # Retornar portas selecionadas e server_dict():
    return mainServer_port, copyServer_port, server_dict, valid_token

def receive_increase_storage(port):
    server_check = TCPManagerServerSocket.recv(BUFFER_SIZE)
    server_check = server_check.decode()
    if(server_check != "False"): 
        TCPManagerServerSocket.send(str.encode(f"Recebi o tamanho de arquivo existente: {server_check} bytes"))
        server_dict[port] += int(server_check) # Incrementa o armazenamento do servidor principal
    else:
        TCPManagerServerSocket.send(str.encode("Recebi que o arquivo não existe."))   

TCPManagerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) # Cria um socket TCP
TCPManagerSocket.bind((DEFAULT_IP, MANAGER_PORT)) # Bind entre socket criado e IP e porta
TCPManagerSocket.listen() # Gerenciador fica escutando
print("GERENCIADOR ATIVADO!")

while True:
    print("Ouvindo...")
    conn, address = TCPManagerSocket.accept() # conexão aceita após solicitação do cliente / server
    print(f"Conexão Estabelecida: {address}")

    while True:
        filesize = conn.recv(BUFFER_SIZE) # Recebo o tamanho do arquivo do cliente
        filesize= filesize.decode()
        
        if(filesize !=  "Arquivo não encontrado!"):
            filesize = int(filesize)
            print(f"Recebi do cliente o tamanho de arquivo {filesize} bytes")
            
            print("Selecionando e validando porta de servidor destino e réplica...")
            mainServer_port, copyServer_port, server_dict, valid_token = select_ports(server_dict, filesize)
            
            # Se Servidor Principal tem armazenamento suficiente pra suportar o arquivo
            if(valid_token != 1):
                msg = str(mainServer_port) + "/client"
        
                print("Mandando porta/token de servidor destino...")
                conn.send(str.encode(msg))
                print(f"{msg} enviada, aguardando transferência ser completa...")
                        
                verifier = conn.recv(BUFFER_SIZE)
                print("[CLIENT]", verifier.decode())
                
                # Solicita conexão ao server:
                TCPManagerServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
                TCPManagerServerSocket.connect((DEFAULT_IP, mainServer_port))
                print("Conectado com servidor principal!")
                
                receive_increase_storage(mainServer_port)
                    
                data = conn.recv(BUFFER_SIZE) # Mensagem recebida que o cliente terminou de enviar o arquivo
                print("Mensagem recebida (CLIENT): ", data.decode())
                
                server_dict[mainServer_port] -= filesize # Decremento o armazenamento do servidor principal
                
                print("------------------MANDAR PORTA RÉPLICA----------------")
                # Se Servidor Réplica tem armazenamento suficiente pra suportar o arquivo
                if(valid_token != 2):
                    print("Enviando porta/token de servidor de destino...")
                    msg = str(copyServer_port) + "/server"
                    TCPManagerServerSocket.send(str.encode(msg)) # Enviar porta ao servidorPrincipal         
                    print(f"{msg} enviada, aguardando transferência ser completa...")                             

                    receive_increase_storage(copyServer_port)
                    
                    data = TCPManagerServerSocket.recv(BUFFER_SIZE) # Mensagem recebida que o servidor terminou de enviar o arquivo
                    print("Mensagem recebida (SERVER): ", data.decode())
                    
                    server_dict[copyServer_port] -= filesize # Decremento o armazenamento do servidor réplica
                    
                    print("SERVIDORES atualizados:")
                    print_dict(server_dict)
                    
                    # Conexão encerrada pelo server
                    
                # Se Servidor Réplica não tem armazenamento suficiente, ninguém abaixo dele tem! Réplica não é possível
                else:
                    print("Mandando mensagem de 'Sem espaço para replicação' para o servidor...")
                    TCPManagerServerSocket.send(str.encode("Sem espaço para replicação"))
                    
            # Se Servidor Principal não tem armazenamento suficiente, ninguém tem! Envio não é possível!
            else:
                print("Mandando mensagem de 'Espaço Insuficiente' para o cliente...")
                conn.send(str.encode("Espaço Insuficiente"))
        # Arquivo não encontrado!
        else:
            print("Mandando mensagem de 'Arquivo não encontrado' para o cliente...")
            conn.send(str.encode("Arquivo não encontrado!"))
        
        print()
        print("Aguardando se o cliente deseja mandar mais algum arquivo...")
        resp = conn.recv(BUFFER_SIZE)
        if (resp.decode().lower() == "s"):
            print("Cliente ENCERROU a conexão")
            conn.close() # Encerrar conexão
            break
        print("Cliente deseja enviar mais um arquivo!")
        print()
        print("###########################################################")
        print()

    off = input("Desligar gerenciador [S/N]? ")
    if (off.lower() == "s"):
        break
    print()