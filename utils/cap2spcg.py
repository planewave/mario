import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
"""
plot spectrograms from captures in a folder
"""

def read_dat(file_path, count=-1, offset=92):

    with open(file_path, 'rb') as f:
        raw = np.fromfile(f, dtype=np.int16, count=count, offset=offset)
    return raw[0::2] + 1j*raw[1::2]

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('folder', type=str, help='folder of the captures')
    args = parser.parse_args()
    crt_fd = Path(args.folder)
    path_gen = crt_fd.glob('*.dat')
    for path in path_gen:
        print(str(path))
        dat = read_dat(path)
        _, ax = plt.subplots(figsize=(14,5))
        ax.specgram(dat, NFFT=512, Fs=56, sides='twosided')
        ax.set_xlabel('time (ms)')
        ax.set_ylabel('frequency (MHz)')
        ax.set_xticklabels(ax.get_xticks() / 1000) # convert us to ms
        ax.set_title(str(path))
        fig_path = str(path.with_suffix('.png'))
        plt.savefig(fig_path)

if __name__ == "__main__":
    main()
