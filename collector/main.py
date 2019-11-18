import sys
from capture import BucketCapture
from frequency import FrequencyCalculator
from client import Client
import logging
import time
import requests

if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
    c=Client('192.168.1.3',4747)
    bc=BucketCapture(['h1-eth1','h1-eth2'],10/11,11)
    flag = False
    delta=0.7
    alpha = 0.45
    fc=FrequencyCalculator(delta=delta,alpha=alpha,minf=2,maxf=20)
    bc.register(fc.calculate_frequency)
    fc.register(c.frequency_send)

    print(f"{alpha}, {delta}")
    requests.post('http://192.168.1.3:8050/reset',json={"alpha":alpha, "delta":delta})
    bc.start()
    c.start()
    time.sleep(5*60)
    requests.post('http://192.168.1.3:8050/reset',json={"alpha":alpha, "delta":delta})
    sys.exit()