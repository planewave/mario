"""
capture quality evaluation
"""

import numpy as np
import argparse


def detect_saturation(file_path, thr_satu=1600):
    with open(file_path, 'rb') as f:
        raw = np.fromfile(f, dtype=np.int16)
    raw = np.abs(raw[52:-1:40])
    satu = (np.sum(raw > thr_satu) / len(raw)) * 100
    return satu


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
