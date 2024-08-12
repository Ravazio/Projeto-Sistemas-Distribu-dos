DEFAULT_IP = "127.0.0.1"
MANAGER_PORT = 5000
BUFFER_SIZE  = 1024

SERVER1_PORT = 6010
SERVER2_PORT = 6020
SERVER3_PORT = 6030
SERVER4_PORT = 6040

CLIENT1_PORT = 7010
CLIENT2_PORT = 7020

basic_info = {"default_IP": "127.0.0.1",
               "manager_port": 5000,
               "buffer_size": 1024
              }
"""
server_dict = {SERVER1_PORT: 50000000,   # 50MB  = 50  * 10^6 B
               SERVER2_PORT: 500000000,  # 500MB = 500 * 10^6 B
               SERVER3_PORT: 1000000000, # 1GB   = 1   * 10^9 B
               SERVER4_PORT: 2000000000  # 2GB   = 2   * 10^9 B
               }
"""
server_dict = {SERVER1_PORT: 50000000,  
               SERVER2_PORT: 10000000, 
               SERVER3_PORT: 20000000, 
               SERVER4_PORT: 40000000  
               }