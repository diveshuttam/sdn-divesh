import requests
import numpy as np
import shlex
import time

command_port = 5000
seeds = [190/1000, 464/1000, 227/1000, 88/1000, 214/1000]
type_arr = ['voip','mpg','pareto','poisson']

type_='poisson'
mins = 5 
timems = 60*mins*1000

def ITGRecv():
    DestHost = 'http://10.0.0.6:5000'
    DestCmd = ['ITGRecv']
    print('ITGRecv')
    d = {
        'command':DestCmd
    }
    a = requests.post(f'{DestHost}/run',json=d)
    print(a.text)



def ITGSend(seed, num):
    SourceHost = 'http://10.0.0.2:5000'
    command_voip = f'ITGSend -s {seed} -a 10.0.0.6 -t {timems} VoIP -x G.711.2 -h RTP -VAD'
    command_mpg = f'cd mpg/{num} && ITGSend {num}.ditg && cd ../..'
    command_pareto = f'ITGSend -s {seed} -a 10.0.0.6 -t {timems} -v 1.16 1'
    command_poisson = f'ITGSend -s {seed} -a 10.0.0.6 -t {timems} -e 2000 -E 122'
    cmd_d = {
        'voip': command_voip,
        'mpg': command_mpg,
        'pareto': command_pareto,
        'poisson': command_poisson
    }
    SrcCmd = shlex.split(cmd_d[type_]) 
    print(SrcCmd)
    d = {
        'command': SrcCmd
    }
    a = requests.post(f'{SourceHost}/run',json=d)
    print(a.text)
    pass

def data_server_reset(alpha,delta,seed):
    controller = 'http://192.168.1.3:8050'
    d = {
        'alpha':alpha,
        'delta':delta,
        'seed':seed,
        'type':type_
    }
    a = requests.post(f'{controller}/reset',json=d)
    pass

def collector_reset(delta,alpha):
    collector = 'http://localhost:5000'
    d = {
        'delta':delta,
        'alpha':alpha
    }
    requests.post(f'{collector}/reset',json=d)
    pass

def controller_reset():
    controller = 'http://192.168.1.3:4747'
    d = {}
    requests.post(f'{controller}/reset', json=d)

def reset_full():
    controller = 'http://192.168.1.3:8050'
    d = {}
    requests.post(f'{controller}/reset_full', json=d)

if __name__ == '__main__':
    for i in range(5):
        reset_full()
        for delta in [0.8]:
            for alpha in [0.85]:
        #for delta in np.arange(0.1,1.0,0.1):
            #for alpha in np.arange(0.05,1.0,0.1):
                ITGRecv()
                time.sleep(1)
                ITGSend(seed=seeds[i], num=i)
                time.sleep(1)
                data_server_reset(alpha, delta, seeds[i])
                time.sleep(1)
                collector_reset(alpha, delta)
                time.sleep(1)
                controller_reset()
                time.sleep(1)

                time.sleep(timems/1000)
