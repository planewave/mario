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
    parser.add_argument('--overwrite', '-o', action='store_true')
    args = parser.parse_args()
    crt_fd = Path(args.folder)
    path_gen = crt_fd.rglob('*.dat')
    for path in path_gen:
        print(str(path))
        dat = read_dat(path)
        fig_path = path.with_suffix('.png')
        if fig_path.exists() and not args.overwrite:
            print('target image exists, skip.')
            continue
        
        _, ax = plt.subplots(3, 1, figsize=(9, 9))
        ax[0].specgram(dat, NFFT=512, Fs=56, noverlap=0, sides='twosided',
                       cmap='viridis')
        ax[0].set_xlabel('time (ms)')
        ax[0].set_ylabel('frequency (MHz)')
        ax[0].set_xticklabels(ax[0].get_xticks() / 1000)  # convert us to ms
        ax[0].set_title(str(path.name))

        ax[1].psd(dat, NFFT=512, Fs=56, noverlap=0)
        ax[1].set_xlabel('frequency (MHz)')

        down_sample = 50
        data = dat[0:-1:down_sample]
        ax[2].plot(np.arange(len(data)) / 56e6 * down_sample * 1000,
                   20 * np.log10(np.abs(data)))
        # ax[2].set_xlim(left=0, right=duration * 1000)
        ax[2].set_ylim(bottom=20, top=100)
        ax[2].axhline(y=70, linestyle='--', color='r')
        ax[2].set_xlabel('time (ms)')
        ax[2].set_ylabel('power (dB)')

        plt.savefig(str(fig_path))
        plt.close('all')


if __name__ == "__main__":
    main()
