import numpy as np

def signlog(x):
    '''Perserve sign wile doing the Log'''
    return np.sign(x) * np.log2(np.abs(x)+1)