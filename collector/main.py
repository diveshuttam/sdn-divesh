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
    bc=BucketCapture(['h1-eth1','h1-eth2'],0.5,20)
    flag = False
    for delta in range(60,90+1,10):
        for alpha in range(85,95+1,10):
            fc=FrequencyCalculator(delta=delta/100,alpha=alpha/100,minf=20,maxf=20)
            bc.register(fc.calculate_frequency)
            fc.register(c.frequency_send)

            print(f"{alpha}, {delta}")
            requests.post('http://192.168.1.3:8050/reset',json={"alpha":alpha/100, "delta":delta/100})
            if(flag == False):
                bc.start()
                c.start()
                flag = True
            time.sleep(60*2)