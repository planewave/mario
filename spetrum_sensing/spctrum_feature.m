close all; clear; clc
addpath ../tools/
filename = '../data/my_device_2020_02_25_11_56_36.dat';
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

%  clustering parameters
r = 40; % local radius   
power_thr = r * 3e4;

seg_len = 56e3/2; % 1ms
n_seg = floor(length(data) / seg_len);
% n_seg = 8;
sig_lib = table;



% loop the sections in the capture
for seg_idx = 1:n_seg
    data_seg = data((1 + (seg_idx - 1) * seg_len):(seg_idx * seg_len));
    psd = periodogram(data_seg, [], nfft, 'centered');
    
%     figure;semilogy(psd);
    
    local_psd_sum = 0;
    sig_flag = false(nfft, 1);
    
    % loop PSD
    sig_in_seg = table;
    sig_idx = 0;
    sig_ended = true;
    for psd_idx = 1:nfft - r
        
        % get local_psd_sum
        if local_psd_sum ~= 0
            local_psd_sum = local_psd_sum - psd(psd_idx - 1) + ...
                psd(psd_idx - 1 + r);
        else % first sum
            local_psd_sum = sum(psd(1:r));
        end
        
        % check power level
        if local_psd_sum > power_thr 
            % login new sig
            if ~sig_flag(psd_idx)
                sig_ended = false;
                sig_idx = sig_idx + 1;
%                 sig_in_seg.freq_low(sig_idx) = psd_idx;
                freq_low = psd_idx;
                
            end
            sig_flag(psd_idx:(psd_idx - 1 + r)) = true;
        % login sig end
        elseif sig_flag(psd_idx) && ~sig_flag(psd_idx + 1)
%             sig_in_seg.freq_high(sig_idx) = psd_idx;
            freq_high = psd_idx;
            
%             sig_in_seg.fc(sig_idx) = (sig_in_seg.freq_high(sig_idx) + ...
%                 sig_in_seg.freq_low(sig_idx)) / 2;
            fc = (freq_high + freq_low) / 2;
            
%             sig_in_seg.bw(sig_idx) = sig_in_seg.freq_high(sig_idx) - ...
%                 sig_in_seg.freq_low(sig_idx);
            bw = freq_high - freq_low;
            sig_in_seg(sig_idx, :) = table(fc, bw);
            sig_ended = true;
%             sig_in_psd(sig_idx).pow = mean(psd(sig_in_psd( ...
%                 sig_idx).freq_low:sig_in_psd(sig_idx).freq_high));      
        end
        
    end
    
    % force signal to end 
    if ~sig_ended
%         sig_in_seg.freq_high(sig_idx) = nfft;
        freq_high = nfft;
%         sig_in_seg.fc(sig_idx) = (sig_in_seg.freq_high(sig_idx) + ...
%             sig_in_seg.freq_low(sig_idx)) / 2;
        fc = (freq_high + freq_low) / 2;
        bw = freq_high - freq_low;
        sig_in_seg(sig_idx, :) = table(fc, bw);
        sig_ended = true;
%         sig_in_seg.bw(sig_idx) = sig_in_seg.freq_high(sig_idx) - ...
%             sig_in_seg.freq_low(sig_idx);
%         sig_ended = true;        
    end
    % check into the sig_lib
    sig_lib = push_siglib(sig_lib, sig_in_seg);

        
    end




% the loops in this function seems redundant, but maybe not that bad
function sig_lib = push_siglib(sig_lib, sig_in_seg)

    fc_thr = 0.04;
    bw_thr = 0.1;
    

    if ~isempty(sig_lib) % we have sig_lib already
 
        for lib_sig_idx = 1:height(sig_lib)
            sig_lib.last_seen(lib_sig_idx) = ...
                sig_lib.last_seen(lib_sig_idx) + 1;
            
            % delete expired sig in lib
            if sig_lib.last_seen(lib_sig_idx) > ...
                    20 * sig_lib.show_time(lib_sig_idx)
                sig_lib.to_delete(lib_sig_idx) = true; 
            end
        end
        
        
        % if there is incoming sig in this seg    
        if ~isempty(sig_in_seg)
            nlib = height(sig_lib);
            for seg_sig_idx = 1:height(sig_in_seg)
                sig_crt = sig_in_seg(seg_sig_idx, :);
                found_crt_in_lib = false;
                for lib_sig_idx = 1:nlib
                    fc_dif = abs(sig_lib.fc(lib_sig_idx) - sig_crt.fc);
                    fc_same = fc_dif < (fc_thr * sig_lib.fc(lib_sig_idx));

                    bw_dif = abs(sig_lib.bw(lib_sig_idx) - sig_crt.bw);
                    bw_same = bw_dif < (bw_thr * sig_lib.bw(lib_sig_idx));
                    
                        
        %             pow_dif = abs(sig_lib(sig_idx).pow - sig_crt.pow);
                    % if the sig_crt is in lib
                    if fc_same && bw_same
                        
                        fc = (sig_lib.fc(lib_sig_idx) * ...
                            sig_lib.show_time(lib_sig_idx) + sig_crt.fc) ...
                            / (sig_lib.show_time(lib_sig_idx) + 1);
                        bw = (sig_lib.bw(lib_sig_idx) * ...
                            sig_lib.show_time(lib_sig_idx) + sig_crt.bw) ...
                            / (sig_lib.show_time(lib_sig_idx) + 1);
                        show_time = sig_lib.show_time(lib_sig_idx) + 1;
                        
                        sig_lib{lib_sig_idx, :} = [fc, bw, show_time, 0, 0];

                        found_crt_in_lib = true;
                        break
                    end
                end
                
                % if the sig_crt is NOT in lib
                if ~found_crt_in_lib
                    sig_lib{nlib + 1, :} = ...
                        [sig_crt.fc, sig_crt.bw, 1, 0, 0];
                   
%                     sig_lib.fc(nlib + 1) = sig_crt.fc;
%                     sig_lib.bw(nlib + 1) = sig_crt.bw;
%                     sig_lib.show_time(nlib + 1) = 1;
%                     sig_lib.last_seen(nlib + 1) = 0;
                end
            end
        end
    
    % init sig_lib with sig_in_seg(1)    
    elseif ~isempty(sig_in_seg)

        sig_lib.fc(1) = sig_in_seg.fc(1);
        sig_lib.bw(1) = sig_in_seg.bw(1);
        sig_lib.show_time(1) = 1;
        sig_lib.last_seen(1) = 0;
        sig_lib.to_delete(1) = false;
    end
    
    if ~isempty(sig_lib)
        sig_lib = sig_lib(~sig_lib.to_delete, :);
    end

end

