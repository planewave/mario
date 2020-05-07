from argparse import ArgumentParser

import torch
from torch.nn import functional as F
from torch import nn

import pytorch_lightning as pl


class LitModel(pl.LightningModule):

    def __init__(self):
        super().__init__()

        self.hparams = hparams
        # It adds them automatically to tensorboard
        # logs under the hparams tab.
        # Lightning will save those hparams to the checkpoint
        # and use them to restore the module correctly.

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

    def training_step(self, batch, batch_idx):
        x, y = batch
        output = self(x)
        loss = F.nll_loss(output, y)
        logs = {'loss': loss}
        return {'loss': loss, 'log': logs}

    def configure_optimizers(self):
        return Adam(self.parameters(), lr=1e-3)

    def val_dataloader(self):
        pass

    def validation_step(self, batch):
        return {'val_loss': loss}

    def test_dataloader(self):
        pass

    def test_step(self, batch, batch_idx):
        return {'val_loss': loss}

    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument('--encoder_layers', type=int, default=12)
        parser.add_argument('--data_path', type=str, default='/some/path')
        return parser


if __name__ == "__main__":
    parser = ArgumentParser()

    # add PROGRAM level args
    # parser.add_argument('--conda_env', type=str, default='some_name')

    # add model specific args
    parser = LitModel.add_model_specific_args(parser)

    # add all the available trainer options to argparse
    # ie: now --gpus --num_nodes ...
    parser = pl.Trainer.add_argparse_args(parser)  # gpus=1
    hparams = parser.parse_args()

    model = LitModel(hparams)
    trainer = pl.Trainer.from_argparse_args(hparams)
    trainer.fit(model)

    # run test set
    # model = LitModel.load_from_checkpoint(PATH)
    # trainer.test()
