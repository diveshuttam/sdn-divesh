"""
This module takes care of calculating frequency of the captured traffic
"""

from . import capture

"""
Class provides hooks to calculate frequency of current traffic
"""
class FrequencyCalculator():
    """
    Initialize the frequency
    @param alpha is the weight given to past
    @param delta is the threashold which determines sensitivity
    """
    def __init__(self,delta,alpha):
        self.current_frequency=0
        self.previous_frequency=0
        self.delta = delta
        self.alpha = alpha
        self.buckets=None
        self.hooks=[]

    """
    This function calculates the frequency when the buckets arrive
    Register this hook on the bucket complete event in capture
    """
    def calculate_frequency(self, buckets):
        pass

    """
    This function registers a hook to after the frequency is calculated
    """
    def register(self,hook):
        self.hooks.append(hook)

if __name__ == '__main__':
    pass