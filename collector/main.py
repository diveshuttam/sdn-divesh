import sys
from capture import BucketCapture
from frequency import FrequencyCalculator
from client import Client
import logging
import time

from flask import Flask, request

app = Flask(__name__)
@app.route('/reset',methods=['POST'])
def reset():
    global bc
    global c
    js = request.json
    delta = js['delta']
    alpha = js['alpha']
    fc=FrequencyCalculator(delta=delta,alpha=alpha,minf=2,maxf=200)
    bc.register(fc.calculate_frequency)
    fc.register(c.frequency_send)
    print(f"{alpha}, {delta}")
    return "done", 201

if __name__ == '__main__':
    global c
    global bc
    c=Client('192.168.1.3',4747)
    bc=BucketCapture(['h1-eth1','h1-eth2'],0.05,200)
    bc.start()
    app.run(host='0.0.0.0',port=5000,debug=True)
    bc.join()
    c.join()