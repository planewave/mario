from scipy import signal
import numpy as np


class Channelizer():
    """Polyphase FFT analysis filter bank

    The Channelizer separates a broadband input signal into multiple
    narrow subbands using a fast Fourier transform (FFT)-based analysis
    filter bank. The filter bank uses a prototype lowpass filter and is
    implemented using a polyphase structure.

    this code is a python implementation of dsp.Channelizer in Matlab
    """

    def __init__(self, n_band=8, n_tap_per_band=12):
        # Stopband Attenuation = 80 dB
        self.kaiser_beta = 7.8562
        self.n_band = n_band
        print('the channelizer has {} bands'.format(n_band))
        self.n_tap_per_band = n_tap_per_band
        print('each band has {} taps'.format(n_tap_per_band))
        self.window_size = n_tap_per_band * n_band
        self.poly_phase_matrix = self._find_poly_phase_matrix()

    def channelize(self, input_sig):
        input_sig = np.array(input_sig)
        self._check_input(input_sig)
        sample_per_band = input_sig.size // self.n_band
        input_reshape = input_sig[:self.n_band * sample_per_band]
        input_reshape = input_reshape.reshape((sample_per_band, self.n_band))
        output_sig = np.zeros_like(input_reshape)
        for band_idx in range(self.n_band):
            output_sig[:, band_idx] = signal.lfilter(
                np.flip(self.poly_phase_matrix[:, band_idx]), 1,
                input_reshape[:, band_idx])
        # don't know why flip the filter, but Matlab did it
        return np.fft.fft(output_sig, axis=1)

    def _find_poly_phase_matrix(self):
        window = signal.windows.kaiser(self.window_size + 1, self.kaiser_beta)
        time = np.arange(-self.window_size / 2,
                         self.window_size / 2 + 1) / self.n_band
        numerator = 1 / self.n_band * window * np.sinc(time)

        # Make sure zeros are exact
        numerator[int(self.window_size / 2) + self.n_band::self.n_band] = 0
        numerator[int(self.window_size / 2) - self.n_band::-self.n_band] = 0

        # add order='F' if want to have the same reshape behavior as Matlab
        return numerator[:-1].reshape(self.n_tap_per_band, self.n_band)

    def _check_input(self, x):
        if x.ndim != 1:
            raise Exception('input dimension should be 1')
        if x.size < self.window_size:
            raise Exception('input should be longer than the window')


if __name__ == "__main__":
    chan = Channelizer(n_band=4, n_tap_per_band=8)
    x = np.arange(32) + 7.0
    print(chan.channelize(x))
