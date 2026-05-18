import importlib
import paho.mqtt.client as mqtt
import numpy as np

import json
import time
import sys
import os
try:
    import torch
except:
    pass

from trainer import read_energy
from callbacks import TrainStopper

global ENERGY_CONSUMPTION
ENERGY_CONSUMPTION = 0.0

global HOST_ENERGY_CONSUMPTION
HOST_ENERGY_CONSUMPTION = 0.0

def read_host_energy():
    file_path = '/sys/class/powercap/intel-rapl:0/energy_uj'
    with open(file_path, 'r') as f:
        content_str = f.read()
    return int(content_str)

def create_object(package, class_name, **atributos):
    try:
        module = importlib.import_module(f"{package}")
        class_ = getattr(module, class_name)
        return class_(**atributos)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

n = len(sys.argv)

# check if client_instaciation_args are present
if n != 4 and n != 5:
    print(
        "correct use: python client.py <broker_address> <name> <id> [client_instanciation_args].")
    exit()

BROKER_ADDR = sys.argv[1]
CLIENT_NAME = sys.argv[2]
CLIENT_ID = int(sys.argv[3])
# MODE = sys.argv[4]
CLIENT_INSTANTIATION_ARGS = {}
if len(sys.argv) == 5 and (sys.argv[4] is not None):
    CLIENT_INSTANTIATION_ARGS = json.loads(sys.argv[4])

trainer_class = CLIENT_INSTANTIATION_ARGS.get("trainer_class")
if trainer_class is None:
    trainer_class = "TrainerMNIST"

selected = False


def default(obj):
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    elif type(obj).__module__ == torch.__name__:
        if isinstance(obj, torch.Tensor):
            return obj.tolist()
    else:
        try:
            from Pyfhel import PyCtxt
            if isinstance(obj, PyCtxt):
                return obj.to_bytes().decode('cp437')
        except:
            pass
    raise TypeError('Tipo não pode ser serializado:', type(obj))


def has_method(o, name):
    return callable(getattr(o, name, None))


class color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD_START = '\033[1m'
    BOLD_END = '\033[0m'
    RESET = "\x1B[0m"


# subscribe to queues on connection
def on_connect(client, userdata, flags, rc):
    subscribe_queues = ['minifed/selectionQueue',
                        'minifed/posAggQueue', 
                        'minifed/stopQueue', 
                        'minifed/serverArgs',
                        'minifed/ask_datasz']
    for s in subscribe_queues:
        client.subscribe(s)


# callback for serverArgs: update the args with new information send by the server, between the round 0 and the round 1.
def on_server_args(client, userdata, message):
    msg = json.loads(message.payload.decode("utf-8"))
    if msg['id'] == CLIENT_NAME:
        if msg['args'] is not None:
            trainer.set_args(msg['args'])
        client.publish('minifed/ready',
                       json.dumps({"id": CLIENT_NAME}, default=default))


"""
callback for selectionQueue: the selection queue is sent by the server; 
the client checks if it's selected for the current round or not. If yes, 
the client trains and send the training results back.
"""
def on_message_selection(client, userdata, message):
    global selected
    global ENERGY_CONSUMPTION
    global HOST_ENERGY_CONSUMPTION
    idl_energy = read_energy()
    host_idle_energy = read_host_energy()

    msg = json.loads(message.payload.decode("utf-8"))
    if msg['id'] == CLIENT_NAME:
        if bool(msg['selected']) == True:
            selected = True
            trainer.n_epochs=msg['n_epochs']


            tgt_acc=msg['tgt_acc']
            time_limit =msg['time_limit']
            trainer_callbacks_classes=[TrainStopper(target_accuracy=tgt_acc, 
                                                    time_limit_sec=time_limit)]

            print(color.BOLD_START + 'new round starting' + color.BOLD_END)
            print(
                f'trainer was selected for training this round and will start training!')
            trainer.train_model(callbacks=trainer_callbacks_classes)

            resp_dict = {'id': CLIENT_NAME, 'weights': trainer.get_weights(
            ), 'num_samples': trainer.get_num_samples()}
            if has_method(trainer, 'get_training_args'):
                resp_dict['training_args'] = trainer.get_training_args()
            response = json.dumps(resp_dict, default=default)
            client.publish('minifed/preAggQueue', response)
            print(f'finished training and sent weights!')
        else:
            selected = False
            print(color.BOLD_START + 'new round starting' + color.BOLD_END)
            print(f'trainer was not selected for training this round')

    actv_energy = read_energy()
    ENERGY_CONSUMPTION += actv_energy - idl_energy

    host_actv_energy = read_host_energy()
    HOST_ENERGY_CONSUMPTION += host_actv_energy - host_idle_energy

# callback for posAggQueue: gets aggregated weights and publish validation results on the metricsQueue
def on_message_agg(client, userdata, message):
    global selected
    global ENERGY_CONSUMPTION
    global HOST_ENERGY_CONSUMPTION

    idl_energy = read_energy()
    host_idl_energy= read_host_energy()

    print(f'received aggregated weights!')
    msg = json.loads(message.payload.decode("utf-8"))
    agg_weights = [np.asarray(w, dtype=np.float32)
                   for w in msg["agg_response"][CLIENT_NAME]["weights"]]
    results = trainer.all_metrics()
    results['selected'] = selected

    actv_energy = read_energy()
    host_actv_energy=read_host_energy()

    ENERGY_CONSUMPTION += actv_energy - idl_energy
    results['energy_consumption'] = ENERGY_CONSUMPTION

    HOST_ENERGY_CONSUMPTION+=host_actv_energy-host_idl_energy
    results['host_energy_consumption'] = HOST_ENERGY_CONSUMPTION*2.8E-10

    response = json.dumps(
        {'id': CLIENT_NAME, "metrics": results}, default=default)
    trainer.update_weights(agg_weights)

    if has_method(trainer, "agg_response_extra_info"):
        trainer.agg_response_extra_info(
            msg["agg_response"][CLIENT_NAME] | msg["agg_response"]['all'])

    print(f'sending eval metrics!\n')
    client.publish('minifed/metricsQueue', response)

    sent_energy = read_energy()
    ENERGY_CONSUMPTION += sent_energy - actv_energy

# callback for stopQueue: if conditions are met, stop training and exit process
def on_message_stop(client, userdata, message):
    print(color.RED + f'received message to stop!')
    trainer.set_stop_true()
    exit()

# callback for ask_datasz: server ask the dataset size
def on_message_ask_datasz(client, userdata, message):
    msg = json.loads(message.payload.decode("utf-8"))
    if msg['id'] == CLIENT_NAME:
        erro=''
        try:
            dataset_size = trainer.get_dataset_size_in_bits()
        except Exception as e:
            erro=str(e)
            dataset_size = 0
        client.publish('minifed/post_datasz',
                       json.dumps({"id": CLIENT_NAME, 'dataset_sz': dataset_size}, default=default))
        

trainer = create_object("trainer", trainer_class, id=CLIENT_ID,
                        name=CLIENT_NAME, args=CLIENT_INSTANTIATION_ARGS)

client = mqtt.Client(str(CLIENT_NAME))
client.connect(BROKER_ADDR, keepalive=0)
client.on_connect = on_connect
client.message_callback_add('minifed/selectionQueue', on_message_selection)
client.message_callback_add('minifed/posAggQueue', on_message_agg)
client.message_callback_add('minifed/stopQueue', on_message_stop)
client.message_callback_add('minifed/serverArgs', on_server_args)
client.message_callback_add('minifed/ask_datasz', on_message_ask_datasz)

# start waiting for jobs
client.loop_start()


response = json.dumps({'id': CLIENT_NAME,
                       'accuracy': trainer.eval_model(), 
                       "metrics": trainer.all_metrics()}, 
                       default=default)

client.publish('minifed/registerQueue',  response)

print(color.BOLD_START +
      f'trainer {CLIENT_NAME} connected!\n' + color.BOLD_END)


while not trainer.get_stop_flag():
    time.sleep(1)

client.loop_stop()
