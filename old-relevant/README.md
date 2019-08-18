# sdn-project

### Export container:
docker export adoring_pasteur > sdn.tar

### Importing container: (sdn.tar is obtained by exporting container above)
docker import sdn.tar

### commiting container
docker commit adoring_pasteur

### saving container
docker save (image name) > sdn.tar

### listing all images (to get image name)
docker images

### listing all docker containers
docker ps -a

### to allow all clients (for x11)
xhost +

### run container from image (sdn-project must be present in home folder, also sdn is the name of image obtained from docker save)

docker run -it -v ~/sdn-project:/root/sdn-project \
-e DISPLAY=$DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix \
sdn

Docker
--------
docker start -i adoring_pasteur
docker exec -it adoring_pasteur /bin/bash

Inside docker (in sdn-project)
-----------------------------
#to activate python virtual environment
source sdn-env/bin/activate 

#create topology
mn --custom bigtopo.py --topo bigtopo --mac --controller remote

#add links & configure ip
py net.addLink(c0, h1)
h1 ifconfig h1-eth3 192.168.1.2 netmask 255.255.255.0
c0 ifconfig c0-eth0 192.168.1.3 netmask 255.255.255.0

#mirror port
ovs-vsctl -- set Bridge s1 mirrors=@m -- --id=@s1-eth1 get Port s1-eth1 -- --id=@s1-eth2 get Port s1-eth2 -- --id=@s1-eth3 get Port s1-eth3 -- --id=@s1-eth4 get Port s1-eth4 -- --id=@m     create Mirror name=mymirror select-dst-port=@s1-eth1,@s1-eth2,@s1-eth3 select-src-port=@s1-eth1,@s1-eth2,@s1-eth3 output-port=@s1-eth4
ovs-vsctl -- set Bridge s3 mirrors=@m -- --id=@s3-eth1 get Port s3-eth1 -- --id=@s3-eth2 get Port s3-eth2 -- --id=@s3-eth3 get Port s3-eth3 -- --id=@s3-eth4 get Port s3-eth4 -- --id=@m     create Mirror name=mymirror select-dst-port=@s3-eth1,@s3-eth2,@s3-eth3 select-src-port=@s3-eth1,@s3-eth2,@s3-eth3 output-port=@s3-eth4

#run the ryu application
ryu-manager ryu.app.controller_monitoring_server

#in h2
cd ditg/bin
./ITGRecv

#in h6
cd ditg/bin
./ITGSend -a 10.0.0.2 -t 2000000 -e 2000 -E 122

#in h1
source sdn-env/bin/activate
cd live_monitoring
python start_mirrored_host_client.py

#for live graph
source sdn-env/bin/activate
python live_graph.py

#switch status
ovs-vsctl show
ovs-dpctl show

#check flow table
ovs-ofctl -O OpenFlow13 dump-flows s1

#tcpdump command for hosts
tcpdump -en -i (interface)
