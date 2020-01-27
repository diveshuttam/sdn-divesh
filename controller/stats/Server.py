"""
This file contains the server that has to be run on controller,
The collector posts the frequency to the host on frequency calculation
"""


import socket
import logging
import struct
from threading import Thread

from flask import Flask, request
app = Flask(__name__)

class Server():
    def __init__(self,HOST,PORT):
        self.hooks=[]
        self.reset_hooks=[]
        @app.route('/update',methods=['POST'])
        def update():
            js = request.json
            freq=js['frequency']
            print(f"got frequency {freq}")
            for hook in self.hooks:
                hook(freq)
            return "done", 201
        
        @app.route('/reset', methods = ['POST','GET'])
        def reset():
            print('reseting')
            for hook in self.reset_hooks:
                hook()
            return "done", 201
                    

        def fun():
            app.run(host=HOST,port=PORT,use_reloader=False)

        self.thread = Thread(target=fun)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def register(self,hook):
        self.hooks.append(hook)

    def register_reset(self,hook):
        assert(hook!=None)
        self.reset_hooks.append(hook)

if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG,
                    datefmt="%H:%M:%S")
    server = Server('0.0.0.0',4747)
    server.start()
    server.join()