"""
This runs on the collector and sends final polling frequency to the controller
"""
import socket
import struct
import time
from threading import Thread
import logging

"""
Client class which runs an client instance on collector
"""
class Client:
    """
    Initialize the IP and Port of the controller server
    """
    def __init__(self,ip,port):
        self.ip=ip
        self.port=port
        # self.url = f"http://{ip}:{port}/"
        self.server_socks=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connected=False
    
    def start(self):
        def start_fun(self):
            while True:
                try:
                    self.server_socks.connect((self.ip, self.port)) # connect to the server
                except:
                    raise
                else:
                    logging.info("client connected to the server")
                    self.connected=True
                    break
        self.thread=Thread(target=start_fun, args=(self,))
        self.thread.start()
        while(not self.connected):
            time.sleep(0.1)
        
    def join(self):
        self.thread.join()
    
    def disconnect(self):
        self.server_socks.close()
        self.connected = False

    """
    Attach this as a hook to fq object of FrequencyCalculation class
    """
    def frequency_send(self,frequency):
        if(self.connected):
            logging.info(f'sending frequency: {frequency}')
            self.server_socks.sendall(struct.pack('!Q',frequency))

if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
    client = Client('0.0.0.0',4747)
    client.start()
    for i in range(10):
        logging.info(f'sending frequency {i}')
        client.frequency_send(i)
    client.disconnect()
    client.join()