from math import sqrt

"""
@param a list of pairs (time,val)
@param b list of pairs (time,val)
"""
def error(a, b):
    # print(a,b)
    if(not(len(a)>2 and len(b)>2)):
        return 0
    
    interval_b = max(a[0][0],b[0][0])
    interval_e = min(a[-1][0],b[-1][0])
    timelist = []
    for val in range(int(interval_b*10),int(interval_e*10+1),5):
        time = val/10
        timelist.append(time)
    
    n = len(timelist)
    a1=[]
    b1=[]
    
    i=0
    for t in timelist:
        # find a append a
        while(t>a[i+1][0]):
            i+=1

        t1,v1 = a[i]
        t2,v2 = a[i+1]

        v = (t-t2)*(v2-v1)/(t2-t1) + v2
        a1.append(v)
        # print("____",t1,t2,t,':',v1,v2,v)

    i=0
    for t in timelist:
        # find b append b
        while(t>b[i+1][0]):
            i+=1

        t1,v1 = b[i]
        t2,v2 = b[i+1]

        v = (t-t2)*(v2-v1)/(t2-t1) + v2
        b1.append(v)

    error_sum = 0
    # print(a1,'\n',b1___),
    for i,j in zip(a1,b1):
        error_sum+=((i-j)*(i-j))
    
    return sqrt(error_sum/n)