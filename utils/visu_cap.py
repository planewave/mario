import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import signal_file_handler as sfh

"""
plot spectrograms, time and frequency domain plots from captures in a folder

usage: python visu_cap.py [folder path] 
-f [target folder to store images, same folder by default]
-o overwrite the exist imagesS 

"""


def visu_for_analysis(capture, fig_path, nfft=512, fs=56):
    data = capture.payload
    _, ax = plt.subplots(3, 1, figsize=(8, 10))
    ax[0].specgram(data, NFFT=nfft, Fc=capture.header.fc_khz/1e3, Fs=fs,
                   noverlap=0, sides='twosided', cmap='viridis')
    ax[0].set_xlabel('time (ms)')
    ax[0].set_ylabel('frequency (MHz)')
    ax[0].set_xticklabels(ax[0].get_xticks() / 1000)  # convert us to ms
    ax[0].set_title('fc: {fc} MHz, fs: {fs} MHz, gain: {g} dB'.format(
        fc=capture.header.fc_khz/1e3, fs=capture.header.fs_khz/1e3,
        g=capture.header.gain_db))

    ax[2].psd(data, NFFT=nfft, Fs=fs, noverlap=0)
    ax[2].set_xlabel('frequency (MHz)')

    down_sample = 50
    data = np.abs(data[0:-1:down_sample])
    data[data < 1] = 1
    time = np.arange(len(data)) / 56e6 * down_sample * 1000
    ax[1].plot(time, 20 * np.log10(data))
    ax[1].set_ylim(bottom=20, top=80)
    ax[1].set_xlim(left=0, right=time[-1])
    ax[1].axhline(y=70, linestyle='--', color='r')
    ax[1].set_xlabel('time (ms)')
    ax[1].set_ylabel('power (dB)')

    plt.savefig(str(fig_path))
    plt.close()
    return 0


def visu_for_label(capture, fig_path, nfft=512, down_sample=20):
    data = capture.payload
    seg_len = nfft * nfft * down_sample
    if len(data) < seg_len:
        print('Warning, capture length too short, skipped')
        return 1
    data_rsp = np.reshape(data[:seg_len], (nfft, -1))
    # down sampling
    data_rsp = data_rsp[:, :nfft]
    data_fft = np.fft.fft(data_rsp, axis=1)
    data_fft = np.fft.fftshift(data_fft, axes=1)
    data_fft = np.flip(data_fft, axis=1)
    pxx = np.abs(data_fft.T)
    pxx[pxx < 1] = 1
    pxx = np.log10(pxx)
    plt.imsave(str(fig_path), pxx, cmap='bone_r')
    return 0


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('folder', type=str,
                        help='folder of the captures')
    parser.add_argument('--overwrite', '-o',
                        action='store_true', default=False)
    parser.add_argument('--target_folder', '-f', type=str,
                        help='specify folder to save spectrograms')
    parser.add_argument('--type', '-t', type=str, choices=[
                        'analysis', 'label'], default='analysis',
                        help='type of visualization to generate')
    args = parser.parse_args()
    crt_fd = Path(args.folder)
    path_gen = crt_fd.rglob('*.dat')
    if args.type == 'analysis':
        visu = visu_for_analysis
    elif args.type == 'label':
        visu = visu_for_label

    if args.target_folder is not None:
        target_folder = Path(args.target_folder)
        target_folder.mkdir(exist_ok=True)

    for path in path_gen:
        print(str(path))
        capture = sfh.CaptureFile(path=str(path))
        if args.target_folder is None:
            fig_path = path.with_suffix('.jpg')
        else:
            fig_path = target_folder / Path(path.name).with_suffix('.jpg')

        if fig_path.exists() and not args.overwrite:
            print('target image exists, skip.')
            continue
        visu(capture, fig_path)


if __name__ == "__main__":
    main()
