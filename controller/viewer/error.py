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

def error(a, b):
    if(len(a)<=2 or len(b)<=2):
        return None
    xa = list(map(lambda x:x[0], a))  
    ya = list(map(lambda x:x[1], a))  
    xb = list(map(lambda x:x[0], b))  
    yb = list(map(lambda x:x[1], b))  

    interval_b = max(xa[0], xb[0])
    interval_e = min(xa[-1], xb[-1])
    # print('interval',interval_b, interval_e,"\n")

    fa = interpolate.interp1d(xa, ya,kind = 'linear')
    fb = interpolate.interp1d(xb, yb,kind = 'linear')

    ls=np.linspace(interval_b,interval_e, max(len(ya),len(yb))*10)
    # print(xa,xb,ls)
    a=ya_ = fa(ls)
    b=yb_ = fb(ls)
    # print("\n--------------------------",ya_, yb_,"\n---------------------------------------------")
    a = (a - np.mean(a)) / max(max(a),abs(min(a)))
    b = (b - np.mean(b)) / max(max(b),abs(min(b)))

    return sum((b-a)**2)