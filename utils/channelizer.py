from scipy import signal
import numpy as np


class Channelizer():
    def __init__(self, n_band=8, n_tap_per_band=12):
        # Stopband Attenuation = 80 dB
        self.kaiser_beta = 7.8562
        self.n_band = n_band
        self.n_tap_per_band = n_tap_per_band
        self.n_window = n_tap_per_band * n_band
        self.poly_phase_matrix = self._find_poly_phase_matrix()

    def _find_poly_phase_matrix(self):
        window = signal.windows.kaiser(self.n_window + 1, self.kaiser_beta)
        time = np.arange(-self.n_window / 2,
                         self.n_window / 2 + 1) / self.n_band
        numerator = 1 / self.n_band * window * np.sinc(time)

        # Make sure zeros are exact
        numerator[int(self.n_window / 2) + self.n_band::self.n_band] = 0
        numerator[int(self.n_window / 2) - self.n_band::-self.n_band] = 0

        # reshape, order='F' to be consistant with matlab
        poly_phase_matrix = np.reshape(
            numerator[0:-1], (self.n_band, self.n_tap_per_band), order='F')
        return poly_phase_matrix

    def channelize(self, x):

        # reshape input

        # filter with polyphase

        pass


if __name__ == "__main__":
    chan = Channelizer(n_tap_per_band=4)
    print(chan.poly_phase_matrix)
