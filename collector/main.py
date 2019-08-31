from capture import BucketCapture
from frequency import FrequencyCalculator
from client import Client

if __name__ == '__main__':
    bc=BucketCapture('enp0s3',0.5,20)
    fc=FrequencyCalculator(delta=0.3,alpha=0.05,minf=3,maxf=20)
    c=Client('0.0.0.0',4747)

    bc.register(fc.calculate_frequency)
    fc.register(c.frequency_send)

    bc.start()
    c.start()

    bc.join()
    c.join()
