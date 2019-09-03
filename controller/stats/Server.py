"""
This file contains the server that has to be run on controller,
The collector posts the frequency to the host on frequency calculation
"""


import socket
import logging
import struct
from threading import Thread

class Server():
    def __init__(self,HOST,PORT):
        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.hooks=[]
           
    def start(self):
        def fun(self):
            self.s.listen()
            logging.info('server started')
            self.conn, self.addr = self.s.accept()
            logging.info(f'Connected by Mirrored Host {self.addr}')
            logging.info('server started')

            while True:
                try:
                    unpacker = struct.Struct('!Q')
                    x=self.conn.recv(unpacker.size)
                    logging.info(x)
                    pollingFreq = unpacker.unpack(x)[0]
                    logging.info(f'Polling Freq : {pollingFreq}')
                    for hook in self.hooks:
                        Thread(target=hook,args=(pollingFreq,)).start()
                except:
                    self.conn.close()
                    logging.debug('closed existing connections, accepting new connections')
                    self.conn, self.addr = self.s.accept()

        self.thread = Thread(target=fun,args=(self,))
        self.thread.start()

    def join(self):
        self.thread.join()

    def register(self,hook):
        self.hooks.append(hook)

if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG,
                    datefmt="%H:%M:%S")
    server = Server('0.0.0.0',4747)
    server.start()
    server.join()