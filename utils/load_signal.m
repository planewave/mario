function [header, data] = load_signal(filename, delta_t_ms)
fid = fopen(filename, 'rb');
v = uint8(fread (fid, 12, 'uint8'));
% len contains +4 is because total_length was excluding length of itself
len = typecast(flipud(v(1:4)), 'uint32') + 4;

if len == 141792040 || len == 20160040
    head_len = 40;
    header.ver = 1;
elseif len == 141792056
    head_len = 56;
    header.ver = 2;
elseif len == 103040072 || len == 47264072 || len == 141792072
    head_len = 72;
    header.ver = 3;
else
    head_len = typecast(flipud(v(5:8)), 'uint32');
    header.ver = typecast(flipud(v(9:12)), 'uint32');
end

% Read the full header raw data and process it
fseek(fid, 0, 'bof');
v = uint8(fread (fid, head_len, 'uint8'));

if header.ver == 1
    p = 0; % len field is already read
    p = p + 4;
    header.sid = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.cfz = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.fs = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.bw = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.gain = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ts = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.tps = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
elseif header.ver == 2
    p = 0; % len field is already read
    p = p + 4;
    header.sid = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.cfz = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.fs = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.bw = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.gain = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ts = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.tps = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.tot_num_ant = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ant_seq_packed = double(typecast(flipud(v(p+1:p+8)), 'uint64'));
    p = p + 8;
    header.ant_seq_unpacked = unpack_ant_seq(header.ant_seq_packed, ...
                                             header.tot_num_ant);

    header.ant_dwell_t_ms = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.capture_id = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
elseif header.ver == 3
    p = 0; % len field is already read
    p = p + 4;
    header.sid = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.cfz = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.fs = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.bw = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.gain = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ts = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.tps = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.tot_num_ant = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ant_seq_packed = double(typecast(flipud(v(p+1:p+8)), 'uint64'));
    p = p + 8;
    header.ant_seq_unpacked = unpack_ant_seq(header.ant_seq_packed, ...
                                             header.tot_num_ant);

    header.ant_dwell_t_ms = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.capture_id = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.capture_mode = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    if header.capture_mode == 0
        header.capture_mode = 'search';
    else
        header.capture_mode = 'track';
    end
    p = p + 4;
    header.drone_search_bitmap = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
elseif header.ver == 4
    p = 0; % len, header_len, and header_version fields are already read
    p = p + 12;
    header.sid = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.cfz = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.fs = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.bw = double(typecast(flipud(v(p+1:p+4)), 'uint32')) * 1e3;
    p = p + 4;
    header.gain = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ts = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.tps = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.fpga_pps = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.fpga_ts = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
    header.fpga_tps = typecast(flipud(v(p+1:p+4)), 'uint32');
    p = p + 4;
    header.pps_flag = typecast(flipud(v(p+1:p+4)), 'uint32');
    p = p + 4;
    header.tot_num_ant = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.ant_seq_packed = double(typecast(flipud(v(p+1:p+8)), 'uint64'));
    p = p + 8;
    header.ant_seq_unpacked = unpack_ant_seq(header.ant_seq_packed, ...
                                             header.tot_num_ant);

    header.ant_dwell_t_ms = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.capture_id = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    p = p + 4;
    header.capture_mode = double(typecast(flipud(v(p+1:p+4)), 'uint32'));
    if header.capture_mode == 0
        header.capture_mode = 'search';
    else
        header.capture_mode = 'track';
    end
    p = p + 4;
    header.drone_search_bitmap = typecast(flipud(v(p+1:p+8)), 'uint64');
    p = p + 8;
else
    assert(false, 'Bad capture header format');
end

% Reading Header is done, now read the data
if nargin > 1
    n_rd_samp = round(delta_t_ms * header.fs / 1000);
     % each sample is 4 bytes, 2 bytes for I, and 2 bytes for Q
    rd_len = n_rd_samp * 4;
else
    rd_len = len - head_len;
end
v = uint8(fread (fid, rd_len, 'uint8'));
fclose(fid);

data_int = double(typecast(v, 'int16'));
data = data_int(1:2:end) + 1j*data_int(2:2:end);

end

function ant_seq = unpack_ant_seq(ant_seq_packed, tot_num_ant)
    ant_seq = zeros(1, tot_num_ant);
    for i = 1:tot_num_ant
        ant_seq(i) = rem(floor(ant_seq_packed / (2^(4*(i-1)))), 16);
    end
end
