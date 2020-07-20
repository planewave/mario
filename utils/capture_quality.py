"""
capture quality evaluation
"""

import numpy as np
import argparse


def detect_saturation(data):
    """
    detect a capture (complex-value) is saturated
    """
    # decimation
    decim_factor = 56
    data = data[0: -1: decim_factor]
    # max downsampling (max pooling)
    window_size = 500
    n_window = np.floor(data.size / window_size)
    data_reshape = np.reshape(data[0: int(window_size * n_window)],
                              [window_size, -1])
    data_max = np.max(np.abs(data_reshape), axis=0)
    # thr = 1600*1.41
    return np.sum(data_max > 2262) / data_max.size


def get_c42(x):
    def moment(x, p, q):
        return np.mean(x ** (p - q) * np.conj(x) ** q)
    x -= np.mean(x)
    c21 = moment(x, 2, 1).real
    c42 = moment(x, 4, 2) - np.abs(moment(x, 2, 0)
                                   ) ** 2 - 2 * moment(x, 2, 1) ** 2
    c42 = c42.real / c21 ** 2
    return c42

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str)
    parser.add_argument('--function', '-f',
                        choices=['saturation', 'background'])
    args = parser.parse_args()

    if args.function == 'saturation':
        satu = detect_saturation(args.file_path)
        print('saturation index: {0:2.1f}'.format(satu))
        if satu > 10:
            print('capture satruated')
        elif satu > 2:
            print('signal saturated')
        else:
            print('no satruration found')
    else:
        print('function nor given or not supported')
