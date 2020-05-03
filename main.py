import argparse

import torch
from torch.nn import functional as F
from torch import nn
import pytorch_lightning as pl
from pytorch_lightning import Trainer


class Net(pl.LightningModule):

    def __init__(self):
        super().__init__()
        # set up layers in the model
        pass

    def forward(self, x):
        # how data flow over layers
        pass
        return x

    def prepare_data(self):
        # stuff here is done once at the very beginning of training
        # before any distributed training starts

        # download stuff
        # save to disk
        # etc...
        pass

    def train_dataloader(self):
        # data transforms
        # dataset creation
        # return a DataLoader
        pass

    def val_dataloader(self):
        pass

    def test_dataloader(self):
        pass

    def configure_optimizers(self):
        return Adam(self.parameters(), lr=1e-3)

    def training_step(self, batch, batch_idx):
        # training loop
        # return logs, loss
        logs = {'loss': loss}
        pass {'loss': loss, 'log': logs}

    def validation_step(self, batch):
        pass

    def validation_epoch_end(self):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100,
                        help="number of epochs")
    parser.add_argument("--batch_size", type=int, default=8,
                        help="size of each image batch")
    args = parser.parse_args()

    net = Net()
    trainer = Trainer(gpus=1)
    trainer.fit(net)
