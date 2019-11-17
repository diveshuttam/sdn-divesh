from math import sqrt
from scipy import interpolate, signal
import numpy as np
"""
@param a list of pairs (time,val)
@param b list of pairs (time,val)
"""
def count_peaks(x):
    x=list(map(lambda a:a[1],x))
    ans = 0
    if(len(x)<3):
        return 0
    for i,j,k in zip(x,x[1:],x[2:]):
        if(j>=max(k,i)):
            ans+=1
    return ans

def correlate(a,b):
    assert(len(b)<=len(a))


def error(a, b):
    if(len(a)<=2 or len(b)<=2):
        return None
    xa = list(map(lambda x:x[0], a))
    ya = list(map(lambda x:x[1], a))  
    xb = list(map(lambda x:x[0], b))
    yb = list(map(lambda x:x[1], b))  

    print('******')

    interval_b = max(xa[0], xb[0])
    interval_e = min(xa[-1], xb[-1])
    total_interval = abs(interval_b-interval_e)
    fa = interpolate.interp1d(xa, ya,kind = 'linear')
    fb = interpolate.interp1d(xb, yb,kind = 'linear')
    ls = np.linspace(interval_b,interval_e,total_interval*10)

    return correlate(fa(ls),fb(ls))