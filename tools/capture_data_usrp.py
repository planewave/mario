"""
This is a stand alone script that captures and saves data using USRP.
The save format is designed to be compatible with the engineD
"""

import os
import sys
import struct
import numpy as np
from pathlib import Path
from datetime import datetime
import argparse


def main(argv):
    if not Path('/usr/local/lib/uhd/examples').is_dir():
        raise Exception('UHD cannot be found')

    parser = argparse.ArgumentParser(
        description='Collect data using USRP. Use `sudo python3` to run')
    parser.add_argument('--folder', '-fd', type=str, default='usrp_capture',
        help='the folder name (under HOME) that save the data')
    parser.add_argument('--device', '-d', type=str, default='my_device',
        help='the device name')
    parser.add_argument('--frequency', '-f', type=float, nargs="+", default=None, 
        help='carrier frequency in Hz')
    parser.add_argument('--band', '-b', choices=['2.4', '5.8', 'all'], default=None,
        help='frequency band, choose from 2.4, 5.8 or all')
    parser.add_argument('--gain', '-g', type=int, default=10)
    parser.add_argument('--iteration', '-i', type=int, default=1)
    parser.add_argument('--duration', '-t', type=int, choices=[211, 460, 633], default=211)
    parser.add_argument('--no_header', '-n', action='store_true')

    args = parser.parse_args()

    device_name  = args.device
    folder = (Path.home()/args.folder)
    folder.mkdir(exist_ok=True)
    if args.band is None and args.frequency is None:
        print('No frequency is provided, use default 2422.3e6 Hz')
        fc_list = [2422.3e6]
    elif args.band is not None and args.frequency is not None:
        raise Exception('ERROR: only one of band or frequency can be set')
    elif args.band == '2.4':
        fc_list = [2422.3e6, 2442.9e6, 2463.5e6]
    elif args.band == '5.8':
        fc_list = [5747.5e6, 5767.5e6, 5787.5e6, 5807.5e6, 5827.5e6]
    elif args.band == 'all':
        fc_list = [2422.3e6, 2442.9e6, 2463.5e6, 5747.5e6, 5767.5e6, 5787.5e6, 5807.5e6, 5827.5e6]
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
    duration = args.duration / 1000    

    iteration = args.iteration # repeat times for each fc
    gain = args.gain

    for freq in fc_list:
        for _ in range(iteration):
            date_time = datetime.now().strftime('_%Y_%m_%d_%H_%M_%S')
            file_path = folder / (device_name + date_time + '.dat')
            usrp_capture([freq, str(duration), str(gain)], str(file_path), total_len-68)
            # if run as root, uncomment the following
            # os.system('chmod 666 {}'.format(str(file_path))) 
            if args.no_header:
                continue

            header = CaptureHeader(version=3, total_len=total_len, sensor_id=int('FFFF', 16),
                            fc_khz=freq/1000, fs_khz=56e3, bw_khz=44.8e3, gain_db=gain,
                            start_time_ticks=0, tps=1, num_ant=8, ant_seq=int('76543210', 16),
                            ant_dwell_time_ms=50, capture_id=123456, capture_mode=1,
                            drone_search_bitmap=int('FFFFFFFFFFFFFFFF',16))

            capture = CaptureFile(header=header, path=file_path)
            capture.save()

def usrp_capture(command_input, file_path, total_len):

    command = '/usr/local/lib/uhd/examples/rx_samples_to_file' \
        ' --freq {} --rate 56e6 --duration {} --gain {} --file {}' \
        .format(*command_input, file_path)

    over_flow = True
    retry = 0
    while over_flow:
        retry = retry + 1
        if retry > 10:
            raise Exception('capture over flow and retry time out.')
        os.system(command)
        over_flow = os.path.getsize(file_path) < total_len # may more than total_len
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
    payload_v3_len_3 = 47264000 # 211 ms total_len=47264068
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

    def get(self):
        '''
        Utility function to get the header information as a dict.

        Arguments:
            None
        Returns:
            [dict]: Dictionary containing header values.
        '''
        return vars(self)


class CaptureFile:
    '''
    Class representation of capture data.
    '''
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
    main(sys.argv[1:])