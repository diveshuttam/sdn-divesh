x = list(open('/media/sf_Divesh_2016A7TS0045P/sop/sdn-divesh/controller/viewer/outputs/output_poisson.txt'))
for i in range(len(x)):
    l=x[i]
    if(x[i].startswith("reseting")):
        d = x[i][10:-2].split(',')
        try:
            print(delta,alpha,e1[1],','.join(map(str.strip,e1[2:])), e2[1], ','.join(map(str.strip,e2[2:])), sep=',')
        except:
            pass
        delta,alpha = (tuple(map(float,d)))
        continue
    elif(x[i].startswith("***error") and "cqmon" in x[i] and "POST" not in x[i]) :
        e1 = x[i].split(' ')
    elif(x[i].startswith("***error") and "nemon" in x[i] and "POST" not in x[i] ):
        e2 = x[i].split(' ')


print(delta,alpha,e1[1],','.join(map(str.strip,e1[2:])), e2[1], ','.join(map(str.strip,e2[2:])), sep=',')
