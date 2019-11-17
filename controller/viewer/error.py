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
    xa = np.array(list(map(lambda x:(((x[0]*10)//5)*5)/10, a)))
    ya = list(map(lambda x:x[1], a))  
    xb = list(map(lambda x:(((x[0]*10)//5)*5)/10, b))  
    yb = list(map(lambda x:x[1], b))  

    print('******')

    # print('interval',interval_b, interval_e,"\n")
    error=float('inf')
    xaorig=xa[:]
    divisions = 3
    interval_b = max(xa[0], xb[0])
    interval_e = min(xa[-1], xb[-1])
    total_interval = abs(interval_b-interval_e)
    fa = interpolate.interp1d(xa, ya,kind = 'linear')
    fb = interpolate.interp1d(xb, yb,kind = 'linear')
    n_sec = 5
    n_s_intervals = int(total_interval/n_sec)

    if(n_s_intervals==0):
        return None
    
    total_error=0
    count=0
    for i in range(n_s_intervals):
        lsa=np.linspace(interval_b+i*n_sec,min((interval_b)+(i+1)*n_sec,interval_e), n_sec*10)
        a=ya_ = fa(lsa)
        error = float('inf')
        for delta in np.linspace(-3,3,13):
            lsb = lsa+delta
            lsb=list(filter(lambda x: x>=interval_b and x<=interval_e, lsa+delta))
            # print(xa,xb,ls)
            b=yb_ = fb(lsb)
            # print("\n--------------------------",ya_, yb_,"\n---------------------------------------------")
            a = (a - np.mean(a)) / max(max(a),abs(min(a)))
            b = (b - np.mean(b)) / max(max(b),abs(min(b)))
            print('length',len(a),len(b))
            a = a[:len(b)]
            b = b[:len(a)]
            print(len(a),len(b))
            ce = sum((b-a)**2)
            error=min(error,ce)
            print('error', ce, delta, i)
        total_error+=error
        count+=1
    return sqrt(total_error/(count*n_sec*10))