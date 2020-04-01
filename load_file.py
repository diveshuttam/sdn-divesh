import os
import pyshark
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from yaml import load, dump

byte_count = 0
def load_file(file_name):
    if f'{file_name}.yaml' not in os.listdir('./pcap'):
        cap = pyshark.FileCapture(f'./pcap/{file_name}.pcap')
        global byte_count
        byte_count = 0
        arr = []
        def new_packet(pkt):
            global byte_count
            byte_count+=int(pkt.captured_length)
            sniff_time = pkt.sniff_time
            arr.append((sniff_time,byte_count))
            print(byte_count)

        cap.apply_on_packets(new_packet)
        data = dump(arr,Dumper=Dumper)
        open(f"./pcap/{file_name}.yaml","w").write(data)
    else:
        data = open(f"./pcap/{file_name}.yaml").read()
        arr = load(data, Loader=Loader)
    return arr
