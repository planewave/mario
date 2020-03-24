close all; clear; clc
addpath ../tools/
filename = '/home/xiao/usrp_capture/my_device_2020_02_25_11_56_36.dat';
[header, data] = load_signal(filename);
stft_win = 1024;
stft_overlap = 512;
stft_nfft = 1024;
stft_fs = header.fs;

% data = data(1:5e6);
% figure
% spectrogram(data, hann(stft_win), stft_overlap, stft_nfft, stft_fs, ...
%     'yaxis', 'centered');

% figure;psd = periodogram(data, [], 2048, 'centered'); semilogy(psd);
%%
nfft = 2048;
fs = 56e6;
r = 40; % local radius
power_thr = r * 3e4;

seg_len = 56e3; % 1ms
n_seg = floor(length(data) / seg_len);
n_seg = 8;
sig_lib = struct([]);

for seg_idx = 1:n_seg
    data_seg = data((1 + (seg_idx - 1) * seg_len):(seg_idx * seg_len));
    psd = periodogram(data_seg, [], nfft, 'centered');
    
%     figure;semilogy(psd);
    
    local_psd_sum = 0;
    sig_flag = false(nfft, 1);
    for psd_idx = 1:nfft - r
        
        % get local_psd_sum
        if local_psd_sum ~= 0
            local_psd_sum = local_psd_sum - psd(psd_idx - 1) + ...
                psd(psd_idx - 1 + r);
        else % first sum
            local_psd_sum = sum(psd(1:r));
        end
        
        % check power level
        if local_psd_sum > power_thr % login new sig
            if ~ sig_flag(psd_idx)
                sig_info.freq_low = psd_idx;
            end
            sig_flag(psd_idx:(psd_idx - 1 + r)) = true;
        elseif sig_flag(psd_idx) && ~sig_flag(psd_idx + 1)% login sig end
            sig_info.freq_high = psd_idx;
            sig_info.fc = (sig_info.freq_high + sig_info.freq_low) / 2;
            sig_info.bw = sig_info.freq_high - sig_info.freq_low;
            sig_info.pow = sum(psd(sig_info.freq_low:sig_info.freq_high));
            % check into the sig_lib
            sig_lib = push_siglib(sig_lib, sig_info);
        end
        
    end
end



function sig_lib = push_siglib(sig_lib, sig_info)
    nlib = length(sig_lib);
    if nlib ~= 0
        for sig_idx = 1:nlib
            
        end
        sig_lib(nlib + 1) = sig_info;
    else % init 
        sig_lib = sig_info;
        sig_lib(1).show_time = 1;
        sig_lib(1).last_seen = 0;
    end
end

