import idx2numpy
import numpy as np

# Carregar imagens
X_train = idx2numpy.convert_from_file('data/MNIST/train-images.idx3-ubyte')
# Carregar labels
y_train = idx2numpy.convert_from_file('data/MNIST/train-labels.idx1-ubyte')

print(y_train[0]) 

todas_labels=y_train
num_classes = len(np.unique(todas_labels))
print(f"Número de classes distintas: {num_classes}")

# Se quiser ver quais são elas:
print(f"As classes são: {np.unique(todas_labels)}")