import os
import sys
import threading
from pathlib import Path
from time import sleep

from mininet.log import info, setLogLevel
from mininet.term import makeTerm

from mn_wifi.sixLoWPAN.link import LoWPAN
from mn_wifi.energy import BitZigBeeEnergy

from containernet.node import DockerP4Sensor
from containernet.cli import CLI
from containernet.energy import Energy
from energy import EnergyFreqBased

from federated.net import MininetFed
from federated.node import ClientSensor, ServerSensor

from api import app,call_sensor, call_network
from server import api_communication

from server import api_communication

import uvicorn
import threading


def topology(server_script,client_script, server_args,client_args,model_inputs,cpu_governor,experiment_name = 'Experiment',n_rounds=20):
    setLogLevel('info')

    t = 4
    if '-10' in sys.argv:
        t = 10

    volume = "/flw"
    volumes = [f"{Path.cwd()}:" + volume, "/tmp/.X11-unix:/tmp/.X11-unix:rw"]

    experiment_config = {
    "ipBase": "10.0.0.0/24",
    "experiments_folder": "Experiment",
    "date_prefix": False
    }

    NUM_CLIENTS = 6

    net = MininetFed(**experiment_config, controller=[], experiment_name=experiment_name,
                     default_volumes=volumes, topology_file=sys.argv[0], )

    path = os.path.dirname(os.path.abspath(__file__))

    json_file = '/root/json/lowpan-storing.json'
    config = path + '/rules/p4_commands.txt'
    args = {'json': json_file, 'switch_config': config}
    mode = 2
    dimage = 'ramonfontes/bmv2:lowpan'

    info('*** Adding Nodes...\n')
    ap1 = net.addAPSensor('ap1', cls=DockerP4Sensor, ip6='fe80::1/64', panid='0xbeef',
                          dodag_root=True, storing_mode=mode, privileged=True,
                          volumes=[path + "/:/root", "/tmp/.X11-unix:/tmp/.X11-unix:rw"],
                          dimage=dimage, cpu_shares=20, netcfg=True, trickle_t=t,
                          loglevel="info",
                          thriftport=50001,  IPBASE="172.17.0.0/24",
                          **args)
    
    srv1 = net.addFlHost('srv1', cls=ServerSensor, script=server_script,
                         args=server_args, 
                         volumes=volumes,
                         dimage='mininetfed:serversensor',
                         ip6='fe80::2/64', panid='0xbeef', trickle_t=t,
                         privileged=True,
                         port_bindings={5000: 5000},
                         )

    clients = []
    for i in range(NUM_CLIENTS):
        client_args['num_samples']=model_inputs['num_samples'][i]
        clients.append(net.addSensor(f'sta{i}', privileged=True,                                      
                                     cls=ClientSensor, script=client_script,
                                     voltage=3.7, #V
                                     battery_capacity=15, #mAh
                                     ip6=f'fe80::{i+3}/64',
                                     numeric_id=i-1,
                                     args=client_args.copy(), volumes=volumes,
                                     dimage='mininetfed:clientsensor'
                                     ))
    
    net.addAutoStop6()

    # h1 = net.addDocker('h1', volumes=[path + "/:/root", "/tmp/.X11-unix:/tmp/.X11-unix:rw"],
                    #    dimage="ramonfontes/grafana", port_bindings={3000: 3000}, ip='192.168.210.1',
                    #    privileged=True,                     #    cpuset_cpus="14")
                    
    info("*** Configuring Propagation Model\n")

    net.configureWifiNodes()

    info('*** Creating links...\n')
    net.addLink(ap1, srv1, cls=LoWPAN)

    net.addLink(ap1, clients[0], cls=LoWPAN)
    net.addLink(ap1, clients[1], cls=LoWPAN)

    net.addLink(clients[0], clients[2], cls=LoWPAN)
    net.addLink(clients[0], clients[4], cls=LoWPAN)

    net.addLink(clients[1], clients[3], cls=LoWPAN)
    net.addLink(clients[1], clients[5], cls=LoWPAN)
    
    # net.addLink(ap1, h1)
    net.addLinkAutoStop(ap1)

    # # h1.cmd('ifconfig h1-eth1 192.168.0.1')
    ap1.cmd('ifconfig ap1-eth2 192.168.0.10')

    info('*** Starting network...\n')
    net.build()
    ap1.start([])
    net.staticArp()

    # ----------------------- Inicia API de comunicação host - server ------------------------
    def pass_network():
        if net is None:
            return RuntimeError("'network' Not implemented")
        return net
    
    def pass_clients():
        if clients is None:
            return RuntimeError("'clients' Not implemented")
        return clients
    
    app.dependency_overrides[call_network] = pass_network
    app.dependency_overrides[call_sensor] = pass_clients

    config=uvicorn.Config(app,host="0.0.0.0",port=8000)
    server= uvicorn.Server(config)

    thread=threading.Thread(target=server.run)
    thread.start()
    sleep(3)
    print("API is running...")
    api_communication.set_cpu_governor(governor=cpu_governor)
    # -----------------------------------------------------------------------------------------

    info("*** Measuring energy consumption\n")
    EnergyFreqBased(net.sensors)
    # Energy(net.sensors)
    # BitZigBeeEnergy(net.sensors)

    info('*** Running devices...\n')
    net.configRPLD(net.sensors + net.apsensors)

    info('*** Running broker...\n')
    ap1.cmd("nohup mosquitto -c /etc/mosquitto/mosquitto.conf &")

    ap1.cmd("bash -c 'tail -f /var/log/mosquitto/mosquitto.log'")

    net.broker_addr = 'fd3c:be8a:173f:8e80::1'

    sleep(1)
    # CLI(net)
    info('*** Server...\n')
    srv1.run(broker_addr=net.broker_addr, experiment_controller=net.experiment_controller)

    sleep(3)

    info('*** Clients...\n')
    for client in clients:
        client.run(broker_addr=net.broker_addr, experiment_controller=net.experiment_controller)

    
    # # h1.cmd("ifconfig h1-eth1 down")

    info('*** Running Autostop...\n')
    net.wait_experiment()
    os.system('pkill -9 -f xterm')
    info('*** Stopping network...\n')
    net.stop()

    server.should_exit=True
    thread.join()
