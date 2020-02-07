
clear
clc


fs = 56e6;
channel = [1];
fc = 861e6;
gain = 25;

samp_frame = 8160; % official default 362
burst = true;    % enable burst
num_frame = 1e3; % Num Frames In Burst

use_b210 = true; 

if use_b210
    rxradio = comm.SDRuReceiver('Platform','B210', ...
                                'SerialNum','31117E3', ...
                                'MasterClockRate', fs, ...
                                'DecimationFactor', 1, ...                            
                                'ChannelMapping', channel, ...
                                'CenterFrequency', fc, ...
                                'Gain', gain, ...
                                'SamplesPerFrame', samp_frame, ...
                                'OutputDataType', 'single', ...
                                'EnableBurstMode', burst, ...
                                'NumFramesInBurst', num_frame);
elseif use_b200
    rxradio = comm.SDRuReceiver('Platform','B200', ...
                                'SerialNum','3195F00', ...
                                'MasterClockRate', fs, ...
                                'DecimationFactor', 1, ...                            
                                'ChannelMapping', channel, ...
                                'CenterFrequency', fc, ...
                                'Gain', gain, ...
                                'SamplesPerFrame', samp_frame, ...
                                'OutputDataType', 'single', ...
                                'EnableBurstMode', burst, ...
                                'NumFramesInBurst', num_frame);
else
    error('device is not chosen correctly');
end
                        
                       
% From 5e6 to 56e6. When using B210 with multiple channels, 
% the clock rate must be no higher than 30.72e6 Hz. 
% This restriction is a hardware limitation for the B210 radios only 
% when using two-channel operations.
num_chann = 32;
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
len = uint32(0);
frame = 0;
num_frames = 1e4;
thres = zeros(1, num_chann);
tic
while frame < num_frames
    % Keep accessing the SDRu System object output until it is valid
    while len <= 0
        [rec_samps, len, overrun] = rxradio();
        if overrun
            disp('over run')
        end
    end

    if len > 0
        chann_samps = channelizer(rec_samps);
    end
    frame = frame + 1;
    len=uint32(0);
    foo = max(abs(chann_samps),[], 2);
    thres = max(thres, foo);
end
toc
%%
release(rxradio);