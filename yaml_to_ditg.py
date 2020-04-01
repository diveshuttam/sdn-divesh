import os
import load_file
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from yaml import load, dump

file_names = ['poission0.2', 'voip0.1', 'voip0.2']

import sys
ip='10.0.0.1'
initgap=10.0
for fname in file_names:
    print(f'generating {fname}')
    sys.stdout.flush()
    traffic=open(f'../pcap/{fname}.yaml')
    data=traffic.read()
    arr = load(data, Loader=Loader)
    try:
        os.mkdir(f'../pcap/{fname}/')
    except FileExistsError:
        pass
    ps=open(f'../pcap/{fname}/{fname}.ps','w')
    idts=open(f'../pcap/{fname}/{fname}.idts','w')
    ditg=open(f'../pcap/{fname}/{fname}.ditg','w')
    
    px = arr[0][0]
    py = 0
    for x,y in arr:
        if(px!=x):
            idts.write(f'{(x.timestamp()-px.timestamp()+initgap):.10f}')
        else:
            idts.write(f'{initgap:.10f}')
        idts.write('\n')
        
        ps.write(f'{y-py}')
        ps.write('\n')
        py=y
    ditg.write(f'-z {len(arr)} -a {ip}  -Fs {fname}.ps  -Ft {fname}.idts -T TCP')
    ditg.write('\n')
    
    traffic.close()
    ditg.close()
    ps.close()
    idts.close()

