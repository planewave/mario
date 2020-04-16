"""
plot the spectrogram of a binary file collected by USRP 
"""
import numpy as np
import matplotlib.pyplot as plt
import argparse


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--rate', type=float, default=56e6, help='sampling rate in Hz')
    parser.add_argument('--fc', type=float, default=0, help='centre frequency in Hz')
    parser.add_argument('file_path', type=str, help='path of the binary file')
    args = parser.parse_args()

    # file_path = '/home/xiao/usrp_capture/my_device_2020_02_05_16_12_27.dat'
    with open(args.file_path, 'rb') as f:
        raw = np.fromfile(f, dtype=np.int16)
    data = raw[0::2] + 1j*raw[1::2]
    power = 20 * np.log10(np.sqrt(np.mean((data * np.conj(data)).real)))
    print('signal power is {p:3.2f} dB'.format(p=power))
    _, ax = plt.subplots(2, 1, figsize=(10,6))
    ax[0].specgram(data, NFFT=4096, Fs=args.rate / 1e6, Fc=args.fc / 1e6, noverlap=2048)
    ax[0].set_xlabel('time (ms)')
    ax[0].set_ylabel('frequency (MHz)')
    ax[0].set_xticklabels(ax[0].get_xticks() / 1000)
    ax[1].psd(data, NFFT=4096, Fs=args.rate, Fc=args.fc, noverlap=2048)
    plt.show()


if __name__ == "__main__":
    main()
