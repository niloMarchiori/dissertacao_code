
from tensorflow.keras.callbacks import Callback
import time

class TrainStopper(Callback):
    def __init__(self, target_accuracy=0.95, time_limit_sec=60, monitor='accuracy'):
        """
        Args:
            target_accuracy (float): Acurácia alvo para parar o treino (ex: 0.95 para 95%).
            time_limit_sec (int): Tempo limite em segundos.
            monitor (str): A métrica a ser monitorada (ex: 'accuracy' ou 'val_accuracy').
        """
        super().__init__()
        self.target_accuracy = target_accuracy
        self.time_limit_sec = time_limit_sec
        self.monitor = monitor
        self.start_time = None

    def on_train_begin(self, logs=None):
        self.start_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        current_acc = logs.get(self.monitor)
        elapsed_time = time.time() - self.start_time

        if current_acc is not None and current_acc >= self.target_accuracy:
            self.model.stop_training = True
            print(f"\n\n--> Alvo atingido! Acurácia: {current_acc:.4f} >= {self.target_accuracy}")

        if elapsed_time > self.time_limit_sec:
            self.model.stop_training = True
            print(f"\n\n--> Tempo limite excedido! Parando após {elapsed_time:.2f}s")

    def __str__(self):
        return f"TrainStopper(target_accuracy={self.target_accuracy}, time_limit_sec={self.time_limit_sec}, monitor='{self.monitor}')"