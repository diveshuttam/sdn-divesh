import os
import load_file
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from yaml import load, dump

file_names = ['poission0.1', 'poission0.2', 'pareto0.1', 'pareto0.2', 'poission_slow0.2', 'voip0.1', 'voip0.2']

import sys
ip='10.0.0.2'
initgap=10.0
for fname in file_names:
    print(f'generating {fname}')
    sys.stdout.flush()
    traffic=open(f'../pcap1/{fname}.yaml')
    data=traffic.read()
    arr = load(data, Loader=Loader)
    try:
        os.mkdir(f'../pcap1/{fname}/')
    except FileExistsError:
        pass
    ps=open(f'../pcap1/{fname}/{fname}.ps','w')
    idts=open(f'../pcap1/{fname}/{fname}.idts','w')
    ditg=open(f'../pcap1/{fname}/{fname}.ditg','w')
    
    px = 0
    py = 0
    for x,y in arr:
        if(px!=0):
            temp = (x.timestamp()-px.timestamp())*1000
            if(temp<0.01):
                temp=0.01
            idts.write(f'{temp:.10f}')
        else:
            idts.write(f'{1000.0:.10f}')
        idts.write('\n')
        px=x
        ps.write(f'{y-py}')
        ps.write('\n')
        py=y
    ditg.write(f'-z {len(arr)} -a {ip}  -Fs {fname}.ps  -Ft {fname}.idts -T UDP')
    ditg.write('\n')
    
    traffic.close()
    ditg.close()
    ps.close()
    idts.close()

