'''
if this still exists for the second hand it is a mistake and you reading this must now legally seek me out and punch me for being stupid
'''

import numpy as np

# log scaling function preserving sign
def signlog(x):
    '''Perserve sign wile doing the Log'''
    return np.sign(x) * np.log2(np.abs(x)+1)