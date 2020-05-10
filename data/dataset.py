import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from pathlib import Path
from PIL import Image
import json


class SpcgDataset(Dataset):

    def __init__(self, data_folder, npix=512, nsubband=4):
        self.data_folder = Path(data_folder)
        label_gen = self.data_folder.glob('*.json')
        self.label_lst = [x for x in label_gen]
        self.npix = npix  # number of pixel
        self.nsubband = nsubband  # number of sub-bands

    def __len__(self):
        return len(self.label_lst)

    def __getitem__(self, idx):
        label_path = self.label_lst[idx]
        with label_path.open() as f:
            label = json.loads(f.read())
        target = torch.zeros(self.nsubband, 2)  # (sub-band, existance and offset)
        for signal in label['shapes']:
            up_freq = signal['points'][0][1]
            down_freq = signal['points'][1][1]
            mid_freq = (up_freq + down_freq) / 2
            pix_subband = self.npix / self.nsubband
            idx_subband = mid_freq // pix_subband
            offset = (mid_freq % pix_subband) / pix_subband  # normalized
            target[idx_subband, :] = torch.tensor([1, offset])

        img_path = self.data_folder / label['imagePath']
        img = transforms.ToTensor()(Image.open(img_path))

        return img, target
