import pathlib
import struct
import numpy as np
import scipy.io as spio


class UsageException(Exception):
    """Raised when attempt is made to instantiate class incorrectly."""

    pass


class HeaderReadException(Exception):
    """Raised when header reading fails."""

    pass


class DataReadException(Exception):
    """Raised when data reading fails."""

    pass


class SpectrogramHeader:
    # 'static' variables
    HEADER_FORMAT = "=BBBBIIIQQIIIIQQIIIIIIffIIBBBBBBBB"
    HEADER_LEN_BYTES = 112
    PAYLOAD_BYTEORDER = "="
    PAYLOAD_FORMAT = "f"

    def __init__(
        self,
        sensor_id,
        capture_id,
        capture_mode,
        start_time_ticks,
        tps,
        fc_khz,
        fs_khz,
        bw_khz,
        gain_db,
        drone_search_bitmap,
        ant_seq,
        ant_dwell_time_ms,
        num_ant,
        nfft,
        window_len,
        overlap_len,
        margin,
        tbin_width_ms,
        fbin_width_khz,
        tbins,
        fbins,
        margin_removed,
        flattened,
        denoised,
        normalised,
        window_type,
    ):

        # the version is 1 for this header format
        self.header_version = np.uint8(1)
        self.reserved_0 = np.uint8(0)
        self.reserved_1 = np.uint8(0)
        self.reserved_2 = np.uint8(0)
        self.sensor_id = np.uint32(sensor_id)
        self.capture_id = np.uint32(capture_id)
        self.capture_mode = np.uint32(capture_mode)
        self.start_time_ticks = np.uint64(start_time_ticks)
        self.tps = np.uint64(tps)
        self.fc_khz = np.uint32(fc_khz)
        self.fs_khz = np.uint32(fs_khz)
        self.bw_khz = np.uint32(bw_khz)
        self.gain_db = np.uint32(gain_db)
        self.drone_search_bitmap = np.uint64(drone_search_bitmap)
        self.ant_seq = np.uint64(ant_seq)
        self.ant_dwell_time_ms = np.uint32(ant_dwell_time_ms)
        self.num_ant = np.uint32(num_ant)
        self.nfft = np.uint32(nfft)
        self.window_len = np.uint32(window_len)
        self.overlap_len = np.uint32(overlap_len)
        self.margin = np.uint32(margin)
        self.tbin_width_ms = np.float(tbin_width_ms)
        self.fbin_width_khz = np.float(fbin_width_khz)
        self.tbins = np.uint32(tbins)
        self.fbins = np.uint32(fbins)
        self.margin_removed = np.uint8(margin_removed)
        self.flattened = np.uint8(flattened)
        self.denoised = np.uint8(denoised)
        self.normalised = np.uint8(normalised)
        self.window_type = np.uint8(window_type)
        self.reserved_3 = np.uint8(0)
        self.reserved_4 = np.uint8(0)
        self.reserved_5 = np.uint8(0)

    def get(self):
        """
        Utility function to get the header information as a dict.

        Arguments:
            None
        Returns:
            [dict]: Dictionary containing header values.
        """
        return vars(self)

    def __repr__(self):
        return "SpectrogramHeader: {}".format(vars(self))


class SpectrogramFile:
    def __init__(self, header=None, payload=None, path=None):
        if header is not None and payload is not None:
            self.header = header
            self.payload = payload
        elif path is not None:
            self.load(path)
        else:
            raise UsageException

    def save(self, dest_path):
        """
        Save spectrogram to disk.
        """
        # save file
        with open(dest_path, "wb") as f:
            # pack bytes in header
            header_bytes = struct.pack(
                SpectrogramHeader.HEADER_FORMAT,
                self.header.header_version,
                self.header.reserved_0,
                self.header.reserved_1,
                self.header.reserved_2,
                self.header.sensor_id,
                self.header.capture_id,
                self.header.capture_mode,
                self.header.start_time_ticks,
                self.header.tps,
                self.header.fc_khz,
                self.header.fs_khz,
                self.header.bw_khz,
                self.header.gain_db,
                self.header.drone_search_bitmap,
                self.header.ant_seq,
                self.header.ant_dwell_time_ms,
                self.header.num_ant,
                self.header.nfft,
                self.header.window_len,
                self.header.overlap_len,
                self.header.margin,
                self.header.tbin_width_ms,
                self.header.fbin_width_khz,
                self.header.tbins,
                self.header.fbins,
                self.header.margin_removed,
                self.header.flattened,
                self.header.denoised,
                self.header.normalised,
                self.header.window_type,
                self.header.reserved_3,
                self.header.reserved_4,
                self.header.reserved_5,
            )
            f.write(header_bytes)
            # pack bytes in payload
            data_bytes = struct.pack(
                SpectrogramHeader.PAYLOAD_BYTEORDER
                + str(self.header.tbins * self.header.fbins)
                + SpectrogramHeader.PAYLOAD_FORMAT,
                *self.payload,
            )
            f.write(data_bytes)

        return dest_path

    def load(self, path):
        """
        Load spectrogram file from disk.
        """
        # read header and data
        with open(path, "rb") as f:
            header = f.read(SpectrogramHeader.HEADER_LEN_BYTES)
            if len(header) != SpectrogramHeader.HEADER_LEN_BYTES:
                raise HeaderReadException

            # parse header bytes, ignoring header version and reserved bytes
            (
                _,
                _,
                _,
                _,
                sensor_id,
                capture_id,
                capture_mode,
                start_time_ticks,
                tps,
                fc_khz,
                fs_khz,
                bw_khz,
                gain_db,
                drone_search_bitmap,
                ant_seq,
                ant_dwell_time_ms,
                num_ant,
                nfft,
                window_len,
                overlap_len,
                margin,
                tbin_width_ms,
                fbin_width_khz,
                tbins,
                fbins,
                margin_removed,
                flattened,
                denoised,
                normalised,
                window_type,
                _,
                _,
                _,
            ) = struct.unpack(SpectrogramHeader.HEADER_FORMAT, header)
            # create header object
            self.header = SpectrogramHeader(
                sensor_id,
                capture_id,
                capture_mode,
                start_time_ticks,
                tps,
                fc_khz,
                fs_khz,
                bw_khz,
                gain_db,
                drone_search_bitmap,
                ant_seq,
                ant_dwell_time_ms,
                num_ant,
                nfft,
                window_len,
                overlap_len,
                margin,
                tbin_width_ms,
                fbin_width_khz,
                tbins,
                fbins,
                margin_removed,
                flattened,
                denoised,
                normalised,
                window_type,
            )

            # each value is a float (4 bytes)
            data_len_bytes = self.header.tbins * self.header.fbins * 4
            data = f.read(data_len_bytes)
            if len(data) != data_len_bytes:
                raise DataReadException

            # parse data bytes
            try:
                self.payload = np.array(
                    struct.unpack(
                        SpectrogramHeader.PAYLOAD_BYTEORDER
                        + str(self.header.tbins * self.header.fbins)
                        + SpectrogramHeader.PAYLOAD_FORMAT,
                        data,
                    )
                )
            except struct.error:
                raise DataReadException

    def get_spectrogram(self, keep_margin=False):
        # reshape the spectrogram for plotting
        spectrogram = (
            np.array(self.payload)
            .reshape(self.header.tbins, self.header.fbins)
            .T
        )
        # roll the image such that the margin is shown at the top and bottom
        spectrogram = np.roll(spectrogram, self.header.margin, axis=0)
        if not keep_margin:
            spectrogram = spectrogram[
                self.header.margin : self.header.fbins - self.header.margin, :
            ]

        return spectrogram


class CaptureHeader:
    # 'static' variables
    HEADER_V1_FORMAT = ">IIIIIIQQ"
    # NOTE: this length includes the 'total_len' field
    HEADER_V1_LEN_BYTES = 40
    HEADER_V2_FORMAT = ">IIIIIIQQIIII"
    # NOTE: this length includes the 'total_len' field
    HEADER_V2_LEN_BYTES = 56
    HEADER_V3_FORMAT = ">IIIIIIQQIQIIIQ"
    # NOTE: this length includes the 'total_len' field
    HEADER_V3_LEN_BYTES = 72
    # NOTE: v4 header length may be variable (?)
    HEADER_V4_FORMAT = ">IIIIIIIIQQQQIIIQIIIQ"
    PAYLOAD_BYTEORDER = "<"
    PAYLOAD_FORMAT = "h"
    # v1 and v2 have the same payload length
    PAYLOAD_V1_LEN_1 = 141792000  # 633 ms
    PAYLOAD_V1_LEN_2 = 20160000  # 90 ms
    PAYLOAD_V2_LEN = 141792000  # 633 ms
    # v3 has three possible payload lengths
    PAYLOAD_V3_LEN_1 = 141792000  # 633 ms
    PAYLOAD_V3_LEN_2 = 103040000  # 460 ms
    PAYLOAD_V3_LEN_3 = 47264000  # 211 ms
    # NOTE: v4 does not have a specified payload length

    # capture modes
    CAPTURE_MODE_SEARCH = 0
    CAPTURE_MODE_TRACK = 1

    def __init__(
        self,
        version,
        total_len,
        sensor_id,
        fc_khz,
        fs_khz,
        bw_khz,
        gain_db,
        start_time_ticks,
        tps,
        num_ant=None,
        ant_seq=None,
        ant_dwell_time_ms=None,
        capture_id=None,
        capture_mode=None,
        drone_search_bitmap=None,
    ):
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
        """
        Utility function to get the header information as a dict.

        Arguments:
            None
        Returns:
            [dict]: Dictionary containing header values.
        """
        return vars(self)

    def __repr__(self):
        return "CaptureHeader: {}".format(vars(self))


class CaptureFile:
    """Class representation of capture data."""

    def __init__(self, header=None, data=None, path=None):
        if header is not None and data is not None:
            self.header = header
            self._data = data
        elif path is not None:
            self.load(path)
        else:
            raise UsageException

    def load(self, path):
        """
        Load capture data.

        Arguments:
            path [str or pathlib.Path]: Path to the capture file.
        """
        # convert to str, in case the input is pathlib.Path
        path = str(path)

        if pathlib.Path(path).suffix == ".mat":
            self._load_mat(path)
            return

        with open(path, "rb") as f:
            # the first element is always an integer written as big-endian
            try:
                total_len = struct.unpack(">I", f.read(4))[0]
            except struct.error:
                # this can happen in 'copy_dat_files', when a file with
                # extension .dat that is actually not a capture file is input
                raise DataReadException

            # this section is intended to match engined/utils/common.h
            # addition of 4 is because 'total_len' does not include its own
            # length
            if total_len + 4 in (
                (
                    CaptureHeader.PAYLOAD_V1_LEN_1
                    + CaptureHeader.HEADER_V1_LEN_BYTES
                ),
                (
                    CaptureHeader.PAYLOAD_V1_LEN_2
                    + CaptureHeader.HEADER_V1_LEN_BYTES
                ),
            ):
                header_version = 1
                header_len_bytes = CaptureHeader.HEADER_V1_LEN_BYTES
            elif total_len + 4 == (
                CaptureHeader.PAYLOAD_V2_LEN
                + CaptureHeader.HEADER_V2_LEN_BYTES
            ):
                header_version = 2
                header_len_bytes = CaptureHeader.HEADER_V2_LEN_BYTES
            elif total_len + 4 in (
                (
                    CaptureHeader.PAYLOAD_V3_LEN_1
                    + CaptureHeader.HEADER_V3_LEN_BYTES
                ),
                (
                    CaptureHeader.PAYLOAD_V3_LEN_2
                    + CaptureHeader.HEADER_V3_LEN_BYTES
                ),
                (
                    CaptureHeader.PAYLOAD_V3_LEN_3
                    + CaptureHeader.HEADER_V3_LEN_BYTES
                ),
            ):
                header_version = 3
                header_len_bytes = CaptureHeader.HEADER_V3_LEN_BYTES
            else:
                try:
                    header_len_bytes = struct.unpack(">I", f.read(4))[0]
                    header_version = struct.unpack(">I", f.read(4))[0]
                except struct.error:
                    # this can happen in 'copy_dat_files', when a file with
                    # extension .dat that is actually not a capture file is
                    # input
                    raise DataReadException

            # rewind
            f.seek(0)
            if header_version == 1:
                header = f.read(header_len_bytes)
                if len(header) != header_len_bytes:
                    # raise exception if read bytes are less than expected
                    raise HeaderReadException

                # parse header bytes
                (
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                ) = struct.unpack(CaptureHeader.HEADER_V1_FORMAT, header)
                # create header object
                self.header = CaptureHeader(
                    header_version,
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                )

                self.header.num_ant = 1
                self.header.ant_seq = 0
                self.header.ant_dwell_time_ms = 633
                self.header.capture_id = 0
                self.header.capture_mode = CaptureHeader.CAPTURE_MODE_SEARCH
                self.header.drone_search_bitmap = 0xFFFFFFFFFFFFFF
            elif header_version == 2:
                header = f.read(header_len_bytes)
                if len(header) != header_len_bytes:
                    # raise exception if read bytes are less than expected
                    raise HeaderReadException

                # parse header bytes
                (
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                    num_ant,
                    ant_seq,
                    ant_dwell_time_ms,
                    capture_id,
                ) = struct.unpack(CaptureHeader.HEADER_V2_FORMAT, header)
                # create header object
                self.header = CaptureHeader(
                    header_version,
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                    num_ant,
                    ant_seq,
                    ant_dwell_time_ms,
                    capture_id,
                )

                self.header.capture_mode = CaptureHeader.CAPTURE_MODE_SEARCH
                self.header.drone_search_bitmap = 0xFFFFFFFFFFFFFF
            elif header_version == 3:
                header = f.read(header_len_bytes)
                if len(header) != header_len_bytes:
                    # raise exception if read bytes are less than expected
                    raise HeaderReadException

                # parse header bytes
                (
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                    num_ant,
                    ant_seq,
                    ant_dwell_time_ms,
                    capture_id,
                    capture_mode,
                    drone_search_bitmap,
                ) = struct.unpack(CaptureHeader.HEADER_V3_FORMAT, header)
                # create header object
                self.header = CaptureHeader(
                    header_version,
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                    num_ant,
                    ant_seq,
                    ant_dwell_time_ms,
                    capture_id,
                    capture_mode,
                    drone_search_bitmap,
                )
            elif header_version == 4:
                header = f.read(header_len_bytes)
                if len(header) != header_len_bytes:
                    # raise exception if read bytes are less than expected
                    raise HeaderReadException

                # parse header bytes
                (
                    total_len,
                    _,
                    _,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                    fpga_pps,
                    fpga_start_time,
                    fpga_tps,
                    pps_flag,
                    num_ant,
                    ant_seq,
                    ant_dwell_time_ms,
                    capture_id,
                    capture_mode,
                    drone_search_bitmap,
                ) = struct.unpack(CaptureHeader.HEADER_V4_FORMAT, header)
                # create header object
                self.header = CaptureHeader(
                    header_version,
                    total_len,
                    sensor_id,
                    fc_khz,
                    fs_khz,
                    bw_khz,
                    gain_db,
                    start_time_ticks,
                    tps,
                    num_ant,
                    ant_seq,
                    ant_dwell_time_ms,
                    capture_id,
                    capture_mode,
                    drone_search_bitmap,
                )
            else:
                raise DataReadException
            # need to subtract 4 because the value of the total_len field does
            # not include its own size. the last 4 bytes in the file are
            # ignored.
            data_len_bytes = self.header.total_len - (header_len_bytes - 4)
            if data_len_bytes < 1:
                raise DataReadException

            data = f.read(data_len_bytes)
            if len(data) != data_len_bytes:
                raise DataReadException

            # each sample is a 2-byte short
            data_len_shorts = data_len_bytes // 2
            try:
                data_int16 = np.array(
                    struct.unpack(
                        self.header.PAYLOAD_BYTEORDER
                        + str(data_len_shorts)
                        + self.header.PAYLOAD_FORMAT,
                        data,
                    )
                )
            except struct.error:
                raise DataReadException

            # save the raw binary data
            self._data = data_int16
            self.payload = data_int16[0::2] + 1j * data_int16[1::2]

    def _load_mat(self, path):
        data = spio.loadmat(path, squeeze_me=True)
        self.header = CaptureHeader(
            0,
            0,
            0,
            data["centerFreq"] * 1e-3,
            data["sampRate"] * 1e-3,
            # NOTE: hardcoding bandwidth until better
            # way can be found
            44800,
            data["sdrRxGain"],
            0,
            0,
        )
        self.payload = data["rxdata"]

    # def save(self, dest_path):
    #     with open(dest_path, "wb") as f:
    #         # pack bytes in header
    #         header_bytes = struct.pack(
    #             self.header.HEADER_V3_FORMAT,
    #             self.header.total_len,
    #             self.header.sensor_id,
    #             self.header.fc_khz,
    #             self.header.fs_khz,
    #             self.header.bw_khz,
    #             self.header.gain_db,
    #             self.header.start_time_ticks,
    #             self.header.tps,
    #             self.header.num_ant,
    #             self.header.ant_seq,
    #             self.header.ant_dwell_time_ms,
    #             self.header.capture_id,
    #             self.header.capture_mode,
    #             self.header.drone_search_bitmap,
    #         )
    #         f.write(header_bytes)
    #         # pack bytes in payload
    #         data_bytes = struct.pack(
    #             CaptureHeader.PAYLOAD_BYTEORDER
    #             + str(len(self._data))
    #             + CaptureHeader.PAYLOAD_FORMAT,
    #             *self._data,
    #         )
    #         f.write(data_bytes)

    def save(
        self,
        dest_path,
        version="v4",
        capture_len=None,
        center_freq=None,
        capture_mode=None,
    ):
        sensor_id = self.header.sensor_id
        if center_freq is not None:
            fc_khz = center_freq
        else:
            fc_khz = self.header.fc_khz
        fs_khz = self.header.fs_khz
        bw_khz = self.header.bw_khz
        gain_db = self.header.gain_db
        start_time_ticks = self.header.start_time_ticks
        tps = self.header.tps
        fpga_pps = 0
        fpga_start_time = 0
        fpga_tps = 0
        pps_flag = 0
        if self.header.header_version == 1:
            num_ant = np.uint32(4)
            ant_seq = np.uint64(int("3210", 16))
            ant_dwell_time_ms = np.uint32(50)
            capture_id = np.uint32(123456)
            capture_mode = np.uint32(0)
            drone_search_bitmap = np.uint64(int("FFFFFFFFFFFFFFFF", 16))
        elif self.header.header_version == 2:
            num_ant = self.header.num_ant
            ant_seq = self.header.ant_seq
            ant_dwell_time_ms = self.header.ant_dwell_time_ms
            capture_id = self.header.capture_id
            capture_mode = np.uint32(0)
            drone_search_bitmap = np.uint64(int("FFFFFFFFFFFFFFFF", 16))
        else:
            num_ant = self.header.num_ant
            ant_seq = self.header.ant_seq
            ant_dwell_time_ms = self.header.ant_dwell_time_ms
            capture_id = self.header.capture_id
            if capture_mode is None:
                capture_mode = self.header.capture_mode
            else:
                capture_mode = np.uint32(capture_mode)
            drone_search_bitmap = self.header.drone_search_bitmap

        # determine the data length
        if capture_len is not None:
            data_length = self.header.fs_khz * capture_len * 2  # number of
            # bytes
        else:
            data_length = len(self._data)
        if version == "v4":
            header_len = np.uint32(
                np.sum(
                    [
                        4 if b == "I" else 8
                        for b in CaptureHeader.HEADER_V4_FORMAT[1:]
                    ]
                )
            )
            total_length = header_len + 2 * data_length - 4  # total_length
            # is not included
            header_version = 4
            header_format = CaptureHeader.HEADER_V4_FORMAT
            header = [
                header_format,
                total_length,
                header_len,
                header_version,
                sensor_id,
                fc_khz,
                fs_khz,
                bw_khz,
                gain_db,
                start_time_ticks,
                tps,
                fpga_pps,
                fpga_start_time,
                fpga_tps,
                pps_flag,
                num_ant,
                ant_seq,
                ant_dwell_time_ms,
                capture_id,
                capture_mode,
                drone_search_bitmap,
            ]
        else:
            raise ValueError("Only support return v4 format capture")

        with open(dest_path, "wb") as f:
            # pack bytes in header
            header_bytes = struct.pack(*header)
            f.write(header_bytes)

            # pack bytes in payload
            data_bytes = struct.pack(
                CaptureHeader.PAYLOAD_BYTEORDER
                + str(len(self._data[:data_length]))
                + CaptureHeader.PAYLOAD_FORMAT,
                *self._data[:data_length],
            )
            f.write(data_bytes)
