from capture import BucketCapture
from frequency import FrequencyCalculator
from client import Client
import logging

if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
    bc=BucketCapture(['h1-eth1','h1-eth2'],0.5,20)
    fc=FrequencyCalculator(delta=0.3,alpha=0.95,minf=3,maxf=20)
    c=Client('192.168.1.3',4747)

    bc.register(fc.calculate_frequency)
    fc.register(c.frequency_send)

    bc.start()
    c.start()

    bc.join()
    c.join()
