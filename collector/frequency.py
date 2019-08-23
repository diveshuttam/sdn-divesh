"""
This module takes care of calculating frequency of the captured traffic
"""

from capture import BucketCapture
import logging

"""
Class provides hooks to calculate frequency of current traffic
"""
class FrequencyCalculator():
    """
    Initialize the frequency
    @param alpha is the weight given to past
    @param delta is the threashold which determines sensitivity
    """
    def __init__(self,delta=0.3,alpha=0.05,minf=3,maxf=20):
        self.current_frequency=0
        self.previous_frequency=0
        self.curr_delta = delta
        self.prev_delta = delta
        self.bucket_change_avg = delta
        self.alpha = alpha
        self.buckets=None
        self.hooks=[]
        self.minf=minf
        self.maxf=maxf

    """
    This function calculates the frequency when the buckets arrive
    Register this hook on the bucket complete event in capture
    """
    def calculate_frequency(self, buckets):
        n=len(buckets)
        count = 0
        sum_change = 0
        for x in range(n-1):
            change = abs((buckets[x]._bytes+1-buckets[x+1]._bytes+1)/(buckets[x]._bytes+1))
            sum_change += change
            if change>=self.curr_delta:
                count+=1
        self.bucket_change_avg = sum_change/(n-1)
        self.prev_delta = self.curr_delta
        self.curr_delta = self.prev_delta*(1-self.alpha) + self.bucket_change_avg*self.alpha
        self.previous_frequency = self.current_frequency
        self.current_frequency = 2*count
        logging.info(f"curr freq: {self.current_frequency}")
        return 2*count


    """
    This function registers a hook to after the frequency is calculated
    """
    def register(self,hook):
        self.hooks.append(hook)

"""
Main to test out the module
"""
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    capture = BucketCapture("enp0s3",0.1,20)
    fq = FrequencyCalculator()
    capture.register(fq.calculate_frequency)
    capture.start()
    capture.join()