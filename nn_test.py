import random, copy, pickle, numpy as np
from numba import njit

from time import time
#import prange
# from numba import prange

@njit
def ReLU(x) -> np.ndarray:
    return np.maximum(0, x)

@njit
def Tanh(x) -> np.ndarray:
    return np.tanh(x)

@njit
def Sigmoid(x) -> np.ndarray:
    return 1./(1+np.exp(-x))

@njit
def Softmax(x) -> np.ndarray: 
    return np.exp(x)/np.sum(np.exp(x))

class NeuralNetwork:
    def __init__(self, layers, parent1 = None, parent2 = None):
        self.layers = np.asarray(layers, dtype=np.int64)

        self.fitness = 0

        if parent1:
            self.genome = np.copy(parent1.genome)
            if parent2:
                self.crossover(parent2)
        else:
            self.genome = np.random.uniform(-1, 1, np.prod(layers) + np.sum(layers[1:]))

    def crossover(self, parent2):
        for i in range(len(self.genome)):
            if random.randint(0,2)>0:
                self.genome[i] = parent2.genome[i]
        #self.tweak(0.1)

    def mutate(self, rate):
        for i in range(len(self.genome)):
            if random.random() < rate:
                self.genome[i] = random.random()
    
    def tweak(self, rate):
        rand_norms = np.random.normal(0, 1, len(self.genome))
        rand_bools = np.random.uniform(0, 1, len(self.genome)) < rate
        self.genome += rand_norms * rand_bools

    def load(self, filename):
        with open(filename, 'rb') as inp:
            return pickle.load(inp)
    def save(self, filename):
        with open(filename, 'wb') as outp:
            pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL)

@njit
def run(genome, layers, input) -> np.ndarray:
    input = np.asarray(input, dtype=np.float64)
    index = 0
    for i in range(1, len(layers)):
        output = np.zeros(layers[i])
        for j in range(layers[i]):
            output[j] = np.dot(input, genome[index:index + layers[i - 1]]) + genome[index + layers[i - 1]]
            index += layers[i - 1] + 1
        if i < len(layers):
            # input = ReLU(output)
            input = Tanh(output)
        else:
            # input = Sigmoid(output)
            input = Tanh(output)
    return input

# @njit
# def run(input, layers) -> np.ndarray:
#     index = 0
#     for i in range(1, len(layers)):
#         output = np.zeros(layers[i])
#         for j in range(layers[i]):
#             output[j] = np.dot(input, genome[index:index + layers[i - 1]]) + genome[index + layers[i - 1]]
#             index += layers[i - 1] + 1
#         input = output
#     return input


if __name__ == "__main__":

    bot = NeuralNetwork([5, 10, 10, 10, 10, 10, 2], None, None)

    layers = np.asarray([5, 10, 10, 10, 10, 10, 2], dtype=np.int64)
    genome = np.random.rand(np.prod(layers) + np.sum(layers[1:]))
    input = np.asarray([1, 2, 3, 4, 5], dtype=np.float64)

    now = time()

    bot = NeuralNetwork([5, 10, 10, 10, 10, 10, 2], None, None)

    for i in range(50_000):

        output = run(bot.genome, bot.layers, input)


    print(50_000/(time() - now))