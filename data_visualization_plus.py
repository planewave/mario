# %%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from pathlib import Path
import utils.signal_file_handler as sfh
# %%
folder = Path('/home/xiao/Downloads/915_mavic2')
if not folder.is_dir():
    raise Exception('can\'t find destination folder')
path_gen = folder.glob('*.dat')
# %%
print('start looping in folder {}'.format(str(folder)))
for path in path_gen:
    print(str(path))
    capture = sfh.CaptureFile(path=str(path))

print('end of folder reached')
# %%
nfft = 512
down_sample = 20

capture = sfh.CaptureFile(path=str(next(path_gen)))
data = capture.payload
data_reshape = np.reshape(
    data[:len(data) - len(data) % (nfft * down_sample)], (-1, nfft * down_sample))
data_reshape = data_reshape[:, :nfft]  # down sampling
data_fft = np.fft.fft(data_reshape, axis=1)
data_fft = np.fft.fftshift(data_fft, axes=1)
data_fft = np.flip(data_fft, axis=1)  # put lower freq in the lower part 
data_fft = np.abs(data_fft.T)
data_fft[data_fft < 1] = 1  # avoid log(0)
data_fft = np.log10(data_fft)

plt.imshow(data_fft)
plt.show()