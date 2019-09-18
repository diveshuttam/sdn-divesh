from math import sqrt

"""
@param a list of pairs (time,val)
@param b list of pairs (time,val)
"""
def error(a, b):
    print(a,b)
    if(not(len(a)>2 and len(b)>2)):
        return 0
    
    interval_b = max(a[0][0],b[0][0])
    interval_e = min(a[-1][0],b[-1][0])
    timelist = []
    for val in range(interval_b*10,interval_e*10+1,5):
        time = val/10
        timelist.append(time)
    
    n = len(timelist)
    a=[]
    b=[]
    
    i=0
    for t in timelist:
        # find a append a
        while(t>a[i+1][0]):
            i+=1

        t1,v1 = a[i]
        t2,v2 = a[i+1]

        v = (t-t2)*(v2-v1)/(t2-t1)
        a.append(v)

    i=0
    for t in timelist:
        # find b append b
        while(t>b[i+1][0]):
            i+=1

        t1,v1 = b[i]
        t2,v2 = b[i+1]

        v = (t-t2)*(v2-v1)/(t2-t1)
        b.append(v)

    error_sum = 0
    for i,j in zip(a,b):
        error_sum+=(i-j)**2
    
    return sqrt(error_sum/n)