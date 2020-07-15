"""
This is a stand alone script that captures and saves data using USRP.
The save format is designed to be compatible with the engineD

to install matplotlib:
sudo apt-get install python3-matplotlib
"""

import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import argparse


def main():
    if not Path('/usr/local/lib/uhd/examples').is_dir():
        raise Exception('UHD cannot be found')

    parser = argparse.ArgumentParser(
        description='Collect data using USRP. \
        Use `python3` (may need root privileges) to run')
    parser.add_argument(
        '--folder', '-fd', type=str, default='usrp_capture',
        help='optional, the folder name (under HOME) that save the data')
    parser.add_argument(
        '--device', '-d', type=str, default='my_device',
        help='optional, the device name')
    parser.add_argument(
        '--rate', '-r', type=float, default=56e6,
        help='Sampling rate in Hz')
    parser.add_argument(
        '--frequency', '-f', type=float, nargs="+", default=None,
        help='carrier frequency in Hz')
    parser.add_argument(
        '--band', '-b', choices=['24', '58', '2458', '800900'], default=None,
        help='choose one frequency band, \
        choose `frequency` or `band` to set up the fc of USRP')
    parser.add_argument(
        '--gain', '-g', type=int, default=10, help='optional, USRP Rx gain')
    parser.add_argument(
        '--iteration', '-i', type=int, default=1,
        help='optional, number of captures for each fc')
    parser.add_argument(
        '--duration', '-t', type=int, choices=[211, 460, 633], default=211,
        help='optional, capture length in milisecond')
    parser.add_argument(
        '--no_header', '-nh', action='store_true',
        help='save raw data without header')
    parser.add_argument(
        '--visualize', '-v', action='store_true',
        help='save visualization with data')
    parser.add_argument(
        '--no_data', '-nd', action='store_true',
        help='don\'t save data file, work with -v')
    args = parser.parse_args()

    device_name = args.device
    folder = (Path.home()/args.folder)
    if not folder.exists():
        os.system('mkdir -m777 {}'.format(str(folder)))

    if args.rate > 56e6 or args.rate < 1e6:
        raise Exception('ERROR: sampling rate should be between 1e6 to 56e6')
    if args.rate != 56e6 and args.no_header is False:
        print('with customized sampling rate, header will not be attached')
        args.no_header = True

    if args.band is None and args.frequency is None:
        print('No frequency is provided, use default 2422.3e6 Hz')
        fc_list = [2422.3e6]
    elif args.band is not None and args.frequency is not None:
        raise Exception('ERROR: only one of band or frequency can be set')
    elif args.band == '24':
        fc_list = [2422.3e6, 2442.9e6, 2463.5e6]
    elif args.band == '58':
        fc_list = [5747.5e6, 5767.5e6, 5787.5e6, 5807.5e6, 5827.5e6]
    elif args.band == '2458':
        fc_list = [2422.3e6, 2442.9e6, 2463.5e6, 5747.5e6,
                   5767.5e6, 5787.5e6, 5807.5e6, 5827.5e6]
    elif args.band == '800900':
        fc_list = [801e6, 831e6, 861e6, 891e6, 921e6]
    else:
        if not isinstance(args.frequency, list):
            fc_list = [args.frequency]
        else:
            fc_list = args.frequency

    if args.duration == 211:
        total_len = 47264068
    elif args.duration == 460:
        total_len = 103040068
    elif args.duration == 633:
        total_len = 141792068
    else:
        raise Exception('unsupported duration')
    if args.no_header:
        total_len = 0  # no need if no header
    duration = args.duration / 1000

    iteration = args.iteration  # repeat times for each fc
    gain = args.gain

    for freq in fc_list:
        for _ in range(iteration):
            date_time = datetime.now().strftime('_%Y_%m_%d_%H_%M_%S')
            file_path = folder / (device_name + date_time + '.dat')
            usrp_capture([freq, str(args.rate), str(duration),
                          str(gain)], str(file_path), total_len-68)
            # if run as root, uncomment the following
            os.system('chmod 666 {}'.format(str(file_path)))
            if args.visualize:
                visualize_data(file_path, args.rate, freq, duration, gain)
            if args.no_data:
                file_path.unlink()
                continue
            if args.no_header:
                continue

            header = CaptureHeader(
                version=3, total_len=total_len, sensor_id=int('1', 16),
                fc_khz=freq/1000, fs_khz=56e3, bw_khz=56e3, gain_db=gain,
                start_time_ticks=0, tps=1, num_ant=1,
                ant_seq=int('76543210', 16),
                ant_dwell_time_ms=int(args.duration),
                capture_id=123456, capture_mode=1,
                drone_search_bitmap=int('FFFFFFFFFFFFFFFF', 16))

            capture = CaptureFile(header=header, path=file_path)
            capture.save()


def visualize_data(file_path, fs, fc, duration, gain):
    with file_path.open() as f:
        raw = np.fromfile(f, dtype=np.int16)
    data = raw[0::2] + 1j*raw[1::2]
    power = 20 * np.log10(np.sqrt(np.mean((data * data.conj()).real)))
    # print('digital power is {p:3.2f} dB'.format(p=power))
    _, ax = plt.subplots(3, 1, figsize=(9, 10))
    ax[0].specgram(data, NFFT=512, Fs=fs/1e6, Fc=fc/1e6)
    ax[0].set_xlabel('time (ms)')
    ax[0].set_xlim(left=0, right=duration*1e6)
    ax[0].set_ylabel('frequency (MHz)')
    ax[0].set_xticklabels(ax[0].get_xticks()/1000)
    ax[2].psd(data, NFFT=512, Fs=fs/1e6, Fc=fc/1e6, noverlap=0)
    ax[2].set_xlabel('frequency (MHz)')
    ax[2].set_ylim(bottom=10, top=75)
    ax[2].set_yticks(np.arange(10, 75, 10))
    down_sample = 50
    data = data[0:-1:down_sample]
    ax[1].plot(np.arange(data.size) / fs * down_sample * 1000,
               20 * np.log10(np.abs(data) + 1e-3))
    ax[1].set_xlim(left=0, right=duration * 1000)
    ax[1].set_ylim(bottom=20, top=100)
    ax[1].axhline(y=93.3, linestyle='--', color='r')
    ax[1].set_xlabel('time (ms)')
    ax[1].set_ylabel('power (dB)')
    ax[0].set_title(
        'fc: {fc} MHz, fs: {fs} MHz, gain: {g} dB, power: {p:3.2f} dB'
        .format(fc=fc/1e6, fs=fs/1e6, g=gain, p=power))
    fig_path = str(file_path.with_suffix('.png'))
    plt.savefig(fig_path)
    plt.close()
    os.system('chmod 666 {}'.format(fig_path))  # in case run as sudo
    # plt.show()


def usrp_capture(command_input, file_path, total_len):

    command = '/usr/local/lib/uhd/examples/rx_samples_to_file' \
        ' --freq {} --rate {} --duration {} --gain {} --file {}' \
        .format(*command_input, file_path)
    over_flow = True
    retry = 0
    while over_flow:
        retry = retry + 1
        if retry > 10:
            raise Exception('capture over flow and retry time out.')
        os.system(command)
        # may more than total_len
        over_flow = os.path.getsize(file_path) < total_len
        # print(os.path.getsize(file_path))


class CaptureHeader:
    # 'static' variables
    header_v1_format = '>IIIIIIQQ'
    # NOTE: this length includes the 'total_len' field
    header_v1_len_bytes = 40
    header_v2_format = '>IIIIIIQQIIII'
    # NOTE: this length includes the 'total_len' field
    header_v2_len_bytes = 56
    header_v3_format = '>IIIIIIQQIQIIIQ'
    # NOTE: this length includes the 'total_len' field
    header_v3_len_bytes = 72
    # NOTE: v4 header length may be variable (?)
    header_v4_format = '>IIIIIIIIQQQQIIIQIIIQ'
    payload_byteorder = '<'
    payload_format = 'h'
    # v1 and v2 have the same payload length
    payload_v1_len = 141792000
    payload_v2_len = 141792000
    # v3 has three possible payload lengths
    payload_v3_len_1 = 141792000
    payload_v3_len_2 = 103040000
    payload_v3_len_3 = 47264000  # 211 ms total_len=47264068
    # NOTE: v4 does not have a specified payload length

    def __init__(self, version, total_len, sensor_id, fc_khz, fs_khz, bw_khz,
                 gain_db, start_time_ticks, tps, num_ant=None, ant_seq=None,
                 ant_dwell_time_ms=None, capture_id=None, capture_mode=None,
                 drone_search_bitmap=None, mat=False):
        self.header_version = version

        # fields in the actual file header
        self.total_len = np.uint32(total_len)
        self.sensor_id = np.uint32(sensor_id)
        self.fc_khz = np.uint32(fc_khz)
        self.fs_khz = np.uint32(fs_khz)
        self.bw_khz = np.uint32(bw_khz)
        self.gain_db = np.uint32(gain_db)
        self.start_time_ticks = np.uint64(start_time_ticks)
        self.tps = np.uint64(tps)

        if self.header_version in (2, 3, 4):
            self.num_ant = np.uint32(num_ant)
            self.ant_seq = np.uint32(ant_seq)
            self.ant_dwell_time_ms = np.uint32(ant_dwell_time_ms)
            self.capture_id = np.uint32(capture_id)

        if self.header_version in (3, 4):
            self.capture_mode = np.uint32(capture_mode)
            self.drone_search_bitmap = np.uint64(drone_search_bitmap)


class CaptureFile:
    '''Class representation of capture data'''

    def __init__(self, header, path):
        self.header = header
        self.path = path

    def save(self):
        with self.path.open('r+b') as f:
            raw_data = f.read()
            f.seek(0)
            # pack bytes in header
            header_bytes \
                = struct.pack(self.header.header_v3_format,
                              self.header.total_len,
                              self.header.sensor_id,
                              self.header.fc_khz,
                              self.header.fs_khz,
                              self.header.bw_khz,
                              self.header.gain_db,
                              self.header.start_time_ticks,
                              self.header.tps,
                              self.header.num_ant,
                              self.header.ant_seq,
                              self.header.ant_dwell_time_ms,
                              self.header.capture_id,
                              self.header.capture_mode,
                              self.header.drone_search_bitmap)
            f.write(header_bytes)
            # pack bytes in payload

            f.write(raw_data)


if __name__ == '__main__':
    main()
