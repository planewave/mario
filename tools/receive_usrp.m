
clear
clc


fs = 56e6;
channel = [1];
fc = 2440e6;
gain = 25;
burst = false;    % enable burst
num_frame = 50; % Num Frames In Burst
samp_frame = 6400; % I guess it is samples per buffer
rxradio = init_rx("b210", fs, channel, fc, gain, samp_frame);


                        
                       
% From 5e6 to 56e6. When using B210 with multiple channels, 
% the clock rate must be no higher than 30.72e6 Hz. 
% This restriction is a hardware limitation for the B210 radios only 
% when using two-channel operations.
num_chann = 64;
channelizer = dsp.Channelizer(num_chann);
%%
% close
% data_buf = zeros(samp_frame*num_frame, length(channel), 'single');
% data_all = zeros(452*22, 1);
% 
% for idx_band = 1:22
% 
%     rxradio.CenterFrequency = 800e6 + (idx_band - 1) * 50e6;
%     for idx=1:num_frame
%         [Y,dataLen,overrun] = step(rxradio);
%         data_buf((idx-1)*samp_frame+1:idx*samp_frame, :) = Y;
%     end
% 
%     % pburg(double(data_buf(:, 1)), 7, 'centered')
% 
%     % plot(real([data_buf(:, 1), data_buf(:, 2)]))
%     % legend('ch1', 'ch2')
% 
%     pxx = pwelch(data_buf, 2048, 1024, 256, 56e6, 'centered');
%     pxx(128) = (pxx(127)+pxx(129))/2;
% 
% end
%%
idx_frame = 0;
num_frame = 50; 
% thres = zeros(1, num_chann);
rec_buffer = zeros(samp_frame * num_frame, 1, 'single');

len = 0;
while idx_frame < num_frame
    % Keep accessing the SDRu System object output until it is valid
    
    while len <= 0
        [rec_samps, len, overrun] = rxradio();
%         if overrun
%             disp('over run')
%         end
    end 
%     if len > 0
%         chann_samps = channelizer(rec_samps);
%     end
    st_idx = idx_frame * samp_frame;
    rec_buffer(st_idx + 1:st_idx+samp_frame) = rxradio(); 
    
    idx_frame = idx_frame + 1;
%     len=uint32(0);
%     foo = max(abs(chann_samps),[], 2);
%     thres = max(thres, foo);
end
% psd = 
% periodogram(rec_buffer, [], 256);
% pburg(double(rec_buffer), 4, 64, 56e6, 'centered');
psd = pburg(rec_buffer, 4, 64, 'centered');
semilogy(psd)
% plot(psd)
ylim([0, 0.1])
% release(rxradio);
%%
function rxradio = init_rx(radio, fs, channel, fc, gain, samp_frame)
burst = false;

if radio == "b210"
    rxradio = comm.SDRuReceiver('Platform','B210', ...
                                'SerialNum','31117E3', ...
                                'MasterClockRate', fs, ...
                                'DecimationFactor', 1, ...                            
                                'ChannelMapping', channel, ...
                                'CenterFrequency', fc, ...
                                'Gain', gain, ...
                                'SamplesPerFrame', samp_frame, ...
                                'OutputDataType', 'single', ...
                                'EnableBurstMode', burst);
elseif radio == "b200"
    rxradio = comm.SDRuReceiver('Platform','B200', ...
                                'SerialNum','3195F00', ...
                                'MasterClockRate', fs, ...
                                'DecimationFactor', 1, ...                            
                                'ChannelMapping', channel, ...
                                'CenterFrequency', fc, ...
                                'Gain', gain, ...
                                'SamplesPerFrame', samp_frame, ...
                                'OutputDataType', 'single', ...
                                'EnableBurstMode', burst);
else
    error('device is not chosen correctly');
end
end