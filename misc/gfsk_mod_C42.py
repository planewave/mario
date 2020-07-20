import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def get_c42(x):
    def moment(x, p, q):
        return np.mean(x ** (p - q) * np.conj(x) ** q)
    x -= np.mean(x)
    c21 = moment(x, 2, 1).real
    c42 = moment(x, 4, 2) - np.abs(moment(x, 2, 0)
                                   ) ** 2 - 2 * moment(x, 2, 1) ** 2
    c42 = c42.real / c21 ** 2
    return c42


def upsample(x, n):
    """
    increase sample rate by integer factor
    y = upsample(x,n) increases the sample rate of x by
    inserting n – 1 zeros between samples.
    input is 1D numpy array
    """
    zo = np.zeros((len(x), n), dtype=x.dtype)
    zo[:, 0] += x
    return zo.flatten()


def gfsk_mod(msg, sps, bt, mi):
    """
    GFSK modulator
    msg: binary message (0 or 1)
    sps: sample per symbel
    bt: bandwidth time product
    mi: modulation index, phase change in one bit.

    the span of Gaussian filter is set to one
    """
    msg = msg * 2 - 1.0
    freq = upsample(msg, sps)
    t = np.arange((-0.5 + 1 / sps / 2), 0.5, 1 / sps)
    shape = norm.cdf(2 * np.pi * bt * (t + 0.5) / np.sqrt(np.log(2))) - \
        norm.cdf(2 * np.pi * bt * (t - 0.5) / np.sqrt(np.log(2)))
    shape = shape / shape.sum()
    freq = np.convolve(freq, shape)
    freq = freq[: msg.size * sps]
    phase = np.zeros_like(freq)
    for idx in range(freq.size - 1):
        phase[idx + 1] = phase[idx] + mi * np.pi * freq[idx]
    return np.exp(1j * phase)


if __name__ == "__main__":
    rng = np.random.default_rng()
    msg = rng.integers(2, size=100)
    bt = 0.3
    mi = 0.5
    sps = 10
    x = gfsk_mod(msg, sps, bt, mi)

    print(get_c42(x))
