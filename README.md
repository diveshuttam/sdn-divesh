# How to run

Open 3 terminals

- terminal 1: 
  - sudo mn --controller remote --mac bigtopo.py --topo bigtopo
  - (Inside mn shell)
    - py net.addLink(c0, h1)
    - h1 ifconfig h1-eth3 192.168.1.2 netmask 255.255.255.0
    - c0 ifconfig c0-eth0 192.168.1.3 netmask 255.255.255.0
    - xterm h1 h1 h2 h6 # this will open 4 xterm terminals we will use these later
 
- terminal 2:
  - cd viewer
  - python3 viewer.py  
  - open localhost:8050 in chrome
 
- terminal 3:
  - cd controller
  - python3 controller.py
  
- xterm h2
  - python3 command_server.py

- xterm h6
  - python3 command_server.py

- xterm h1 # 1st
  - cd collector
  - python3 main.py
  
- xterm h1 # 2nd/different one
  - cd collector
  - `# before running the following command, change the experments.py file, it contains parameters to control the experiments to run`
  - python3 experiments.py
