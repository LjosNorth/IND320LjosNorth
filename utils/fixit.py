import numpy as np

# log scaling function preserving sign
def signlog(x):
    '''Perserve sign wile doing the Log'''
    return np.sign(x) * np.log2(np.abs(x)+1)