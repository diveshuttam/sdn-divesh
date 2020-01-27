"""
This runs on the collector and sends final polling frequency to the controller
"""
import socket
import struct
import time
from threading import Thread
import logging
import requests

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
        self.url = f"http://{ip}:{port}/update"
        self.server_socks=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    def join(self):
        self.thread.join()
    
    def disconnect(self):
        self.server_socks.close()
        self.connected = False

    """
    Attach this as a hook to fq object of FrequencyCalculation class
    """
    def frequency_send(self,frequency):
        logging.info(f'sending frequency: {frequency}')
        d = {
            'frequency': frequency
        }
        requests.post(self.url,json=d)

if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
    client = Client('0.0.0.0',4747)
    for i in range(10):
        logging.info(f'sending frequency {i}')
        client.frequency_send(i)
    client.disconnect()
    client.join()