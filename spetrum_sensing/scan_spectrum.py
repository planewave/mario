import uhd
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.signal import welch

if __name__ == "__main__":
    num_samps = 2**14
    samp_rate = 56e6
    freq = 2430e6
    # freq_list = [x for x in range(int(825e6), int(3000e6), int(50e6))]
    usrp = uhd.usrp.MultiUSRP()
    
    # tic = time.time()
    # for freq in freq_list:
    #     samps = usrp.recv_num_samps(num_samps, freq, samp_rate)
    #     print('\n freq: {} MHz, samples: {}'.format(freq / 1e6, samps.shape))
    
    # elapsed = time.time() - tic
    # print('{} loops, {} sec used'.format(len(freq_list), elapsed))
    nfft = 256
    fft_historty = 20
    previous_spcg = np.zeros((fft_historty, nfft))
    current_spcg = np.zeros((fft_historty, nfft))
    plt.ion()
    fig, ax = plt.subplots(figsize=(10,5))
    x = np.linspace(freq - samp_rate / 2, freq + samp_rate / 2, nfft) / 1e6
    y = np.arange(fft_historty)

    for itr in range(1000):
    # while(True):
        plt.cla()
        samps = np.squeeze(usrp.recv_num_samps(num_samps, freq, samp_rate))
        f, pxx = welch(samps,  nperseg=nfft, return_onesided=False)
        pxx = np.fft.fftshift(pxx)
        current_spcg[0, :] = np.log10(pxx)
        current_spcg[1:, :] = previous_spcg[0:-1, :]
        previous_spcg = current_spcg.copy()
        # ax.psd(samps, NFFT=1024, noverlap=512, Fs=samp_rate)
        # plt.plot(np.abs(samps))
        # plt.specgram(samps, NFFT=1024, Fs=samp_rate/1000, noverlap=512,sides='twosided')
        # ax.imshow()
        ax.pcolormesh(x, y, current_spcg)
        plt.pause(0.1)

# plt.ioff()
# plt.show()        