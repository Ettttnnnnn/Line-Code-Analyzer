classdef LineCodeAnalyzerApp < handle
    % LINE CODE ANALYZER - SP25 DIGITAL COMMUNICATION GROUP PROJECT
    % Author: Rohit Kumar Choubey - IIT Madras BS Degree Program
    
    properties (Access = private)
        UIFigure             matlab.ui.Figure
        BinaryEditField      matlab.ui.control.EditField
        LineCodeDropDown     matlab.ui.control.DropDown
        FilterDropDown       matlab.ui.control.DropDown
        SPSSpinner           matlab.ui.control.Spinner
        SNREditField         matlab.ui.control.NumericEditField
        BtEditField          matlab.ui.control.NumericEditField
        RolloffEditField     matlab.ui.control.NumericEditField
        RunButton            matlab.ui.control.Button
        EnergyLabel          matlab.ui.control.Label
        PowerLabel           matlab.ui.control.Label
        TabGroup             matlab.ui.container.TabGroup
        TabOversampled       matlab.ui.container.Tab
        TabLineCode          matlab.ui.container.Tab
        TabFilterCompare     matlab.ui.container.Tab
        TabFiltered          matlab.ui.container.Tab
        TabPSD               matlab.ui.container.Tab
        TabEye               matlab.ui.container.Tab
        AxesBinary           matlab.ui.control.UIAxes
        AxesOversampled      matlab.ui.control.UIAxes
        AxesLineCode         matlab.ui.control.UIAxes
        AxesFilterCompare    matlab.ui.control.UIAxes
        AxesFiltered         matlab.ui.control.UIAxes
        AxesPSD              matlab.ui.control.UIAxes
        AxesEye              matlab.ui.control.UIAxes
    end

    methods (Access = public)
        function app = LineCodeAnalyzerApp()
            app.createUI();
            app.runAnalysis();
        end
    end

    methods (Access = private)
        function createUI(app)
            app.UIFigure = uifigure('Name', 'Line Code Analyzer - SP25 (IIT Madras)', ...
                'Position', [100, 100, 1100, 650]);
            
            pnlControl = uipanel(app.UIFigure, 'Title', 'Simulation Controls', ...
                'Position', [20, 20, 280, 610], 'FontWeight', 'bold');
            
            uilabel(pnlControl, 'Position', [15, 545, 120, 22], 'Text', 'Binary Input:');
            app.BinaryEditField = uieditfield(pnlControl, 'text', ...
                'Position', [125, 545, 135, 22], 'Value', '100101111001');

            uilabel(pnlControl, 'Position', [15, 500, 120, 22], 'Text', 'Line Code:');
            app.LineCodeDropDown = uidropdown(pnlControl, ...
                'Position', [125, 500, 135, 22], ...
                'Items', {'Manchester', 'NRZ', 'RZ'}, 'Value', 'Manchester');

            uilabel(pnlControl, 'Position', [15, 455, 120, 22], 'Text', 'Pulse Shaping:');
            app.FilterDropDown = uidropdown(pnlControl, ...
                'Position', [125, 455, 135, 22], ...
                'Items', {'Gaussian', 'RRC', 'Rectangular'}, 'Value', 'Gaussian');

            uilabel(pnlControl, 'Position', [15, 410, 120, 22], 'Text', 'Samples/Symbol:');
            app.SPSSpinner = uispinner(pnlControl, ...
                'Position', [125, 410, 135, 22], 'Limits', [8, 100], 'Value', 50);

            uilabel(pnlControl, 'Position', [15, 365, 120, 22], 'Text', 'Channel SNR (dB):');
            app.SNREditField = uieditfield(pnlControl, 'numeric', ...
                'Position', [125, 365, 135, 22], 'Value', 20);

            uilabel(pnlControl, 'Position', [15, 320, 120, 22], 'Text', 'Gaussian BT:');
            app.BtEditField = uieditfield(pnlControl, 'numeric', ...
                'Position', [125, 320, 135, 22], 'Value', 0.50);

            uilabel(pnlControl, 'Position', [15, 275, 120, 22], 'Text', 'RRC Roll-off (\alpha):');
            app.RolloffEditField = uieditfield(pnlControl, 'numeric', ...
                'Position', [125, 275, 135, 22], 'Value', 0.35);

            app.RunButton = uibutton(pnlControl, 'push', ...
                'Position', [15, 215, 245, 35], 'Text', 'Run Analysis', ...
                'FontWeight', 'bold', 'BackgroundColor', [0.12, 0.47, 0.71], ...
                'FontColor', 'w', 'ButtonPushedFcn', @(~,~) app.runAnalysis());

            pnlMetrics = uipanel(pnlControl, 'Title', 'Calculated Metrics', ...
                'Position', [15, 15, 245, 180], 'FontWeight', 'bold');
            
            app.EnergyLabel = uilabel(pnlMetrics, ...
                'Position', [10, 110, 225, 30], 'Text', 'Total Energy: -- J', ...
                'FontWeight', 'bold', 'WordWrap', 'on');
            
            app.PowerLabel = uilabel(pnlMetrics, ...
                'Position', [10, 40, 225, 30], 'Text', 'Average Power: -- W', ...
                'FontWeight', 'bold', 'WordWrap', 'on');

            app.TabGroup = uitabgroup(app.UIFigure, 'Position', [310, 20, 770, 610]);
            
            % Tabs corresponding to report figures
            app.TabOversampled   = uitab(app.TabGroup, 'Title', 'Fig 2: Binary vs Oversampled');
            app.TabLineCode      = uitab(app.TabGroup, 'Title', 'Fig 3: Line Code');
            app.TabFilterCompare = uitab(app.TabGroup, 'Title', 'Fig 4: Filter Comparison');
            app.TabFiltered      = uitab(app.TabGroup, 'Title', 'Received (AWGN)');
            app.TabPSD           = uitab(app.TabGroup, 'Title', 'PSD Spectrum');
            app.TabEye           = uitab(app.TabGroup, 'Title', 'Eye Diagram');

            % Subplots for Tab 1 (Figure 2)
            app.AxesBinary      = uiaxes(app.TabOversampled, 'Position', [40, 310, 700, 240]);
            app.AxesOversampled = uiaxes(app.TabOversampled, 'Position', [40, 40,  700, 240]);

            % Single Axes for Remaining Tabs
            app.AxesLineCode      = uiaxes(app.TabLineCode,      'Position', [40, 40, 700, 510]);
            app.AxesFilterCompare = uiaxes(app.TabFilterCompare, 'Position', [40, 40, 700, 510]);
            app.AxesFiltered      = uiaxes(app.TabFiltered,      'Position', [40, 40, 700, 510]);
            app.AxesPSD           = uiaxes(app.TabPSD,           'Position', [40, 40, 700, 510]);
            app.AxesEye           = uiaxes(app.TabEye,           'Position', [40, 40, 700, 510]);
        end

        function runAnalysis(app)
            binaryStr  = strtrim(app.BinaryEditField.Value);
            lineCode   = app.LineCodeDropDown.Value;
            filterType = app.FilterDropDown.Value;
            sps        = app.SPSSpinner.Value;
            SNR_dB     = app.SNREditField.Value;
            BT         = app.BtEditField.Value;
            rolloff    = app.RolloffEditField.Value;

            Fs   = 48000;
            span = 8;
            Tb   = sps / Fs;
            Rb   = 1 / Tb;

            if isempty(binaryStr) || ~all(binaryStr == '0' | binaryStr == '1')
                uialert(app.UIFigure, 'Please provide a valid binary string containing only 0s and 1s.', 'Input Error');
                return;
            end
            bits = binaryStr - '0';

            % --- Figure 2: Binary vs Oversampled Representation ---
            cla(app.AxesBinary);
            stem(app.AxesBinary, 0:length(bits)-1, bits, 'filled', 'LineWidth', 1.5, 'Color', [0.85 0.33 0.10]);
            grid(app.AxesBinary, 'on');
            title(app.AxesBinary, 'Figure 2(a): Original Binary Input Sequence');
            xlabel(app.AxesBinary, 'Bit Index'); ylabel(app.AxesBinary, 'Logic Level');
            app.AxesBinary.XLim = [-0.5, length(bits)-0.5];
            app.AxesBinary.YLim = [-0.2, 1.2];

            oversampled_raw = rectpulse(2*bits - 1, sps);
            t_over = (0:length(oversampled_raw) - 1) / sps;
            
            cla(app.AxesOversampled);
            plot(app.AxesOversampled, t_over, oversampled_raw, 'LineWidth', 1.5, 'Color', [0.12 0.47 0.71]);
            grid(app.AxesOversampled, 'on');
            title(app.AxesOversampled, sprintf('Figure 2(b): Oversampled Discrete-Time Representation (sps = %d)', sps));
            xlabel(app.AxesOversampled, 'Time (Bit Periods)'); ylabel(app.AxesOversampled, 'Amplitude (V)');
            app.AxesOversampled.XLim = [0, length(bits)];
            app.AxesOversampled.YLim = [-1.3, 1.3];

            % --- Line Encoding Stage ---
            switch upper(lineCode)
                case 'NRZ'
                    symbols = 2 * bits - 1;
                    lineCodedSig = rectpulse(symbols, sps);
                case 'RZ'
                    symbols = 2 * bits - 1;
                    rzPulse = [ones(1, floor(sps/2)), zeros(1, sps - floor(sps/2))];
                    lineCodedSig = kron(symbols, rzPulse);
                case 'MANCHESTER'
                    symbols = 2 * bits - 1;
                    manchPulse = [ones(1, floor(sps/2)), -ones(1, sps - floor(sps/2))];
                    lineCodedSig = kron(symbols, manchPulse);
                    zeroMask = kron(bits == 0, ones(1, sps));
                    lineCodedSig(zeroMask == 1) = -lineCodedSig(zeroMask == 1);
            end

            % --- Figure 3: Line-Coded Waveform ---
            cla(app.AxesLineCode);
            t_lc = (0:length(lineCodedSig) - 1) / sps;
            plot(app.AxesLineCode, t_lc, lineCodedSig, 'LineWidth', 1.5, 'Color', [0.12 0.47 0.71]);
            grid(app.AxesLineCode, 'on');
            title(app.AxesLineCode, sprintf('Figure 3: %s Line-Coded Baseband Waveform', lineCode));
            xlabel(app.AxesLineCode, 'Time (Bit Periods)'); ylabel(app.AxesLineCode, 'Amplitude (V)');
            app.AxesLineCode.YLim = [-1.3, 1.3];

            % --- Figure 4: Effect of Pulse-Shaping Filters ---
            cla(app.AxesFilterCompare);
            hold(app.AxesFilterCompare, 'on');
            
            sig_rect = lineCodedSig; 
            h_gauss = gaussdesign(BT, span, sps);
            sig_gauss = conv(lineCodedSig, h_gauss, 'same');
            h_rrc = rcosdesign(rolloff, span, sps, 'sqrt');
            sig_rrc = conv(lineCodedSig, h_rrc, 'same');

            t_comp = (0:length(lineCodedSig)-1) / sps;
            plot(app.AxesFilterCompare, t_comp, sig_rect, 'k--', 'LineWidth', 1.2, 'DisplayName', 'Unfiltered (Rectangular)');
            plot(app.AxesFilterCompare, t_comp, sig_gauss, 'b-', 'LineWidth', 1.6, 'DisplayName', sprintf('Gaussian (BT = %.2f)', BT));
            plot(app.AxesFilterCompare, t_comp, sig_rrc, 'r-', 'LineWidth', 1.6, 'DisplayName', sprintf('RRC (\\alpha = %.2f)', rolloff));

            hold(app.AxesFilterCompare, 'off');
            grid(app.AxesFilterCompare, 'on');
            legend(app.AxesFilterCompare, 'Location', 'northeast');
            title(app.AxesFilterCompare, 'Figure 4: Effect of Pulse-Shaping Filters on Transmitted Waveform');
            xlabel(app.AxesFilterCompare, 'Time (Bit Periods)'); ylabel(app.AxesFilterCompare, 'Amplitude (V)');
            app.AxesFilterCompare.XLim = [0, length(bits)];

            % --- Active Selected Filter Channel & AWGN ---
            switch upper(filterType)
                case 'RECTANGULAR', shapedSig = sig_rect;
                case 'GAUSSIAN',    shapedSig = sig_gauss;
                case 'RRC',         shapedSig = sig_rrc;
            end
            rxSignal = awgn(shapedSig, SNR_dB, 'measured');

            % --- Calculated Metrics ---
            totalEnergy = sum(abs(rxSignal).^2) / Fs;
            avgPower    = mean(abs(rxSignal).^2);
            app.EnergyLabel.Text = sprintf('Total Energy:\n%.6e J', totalEnergy);
            app.PowerLabel.Text  = sprintf('Average Power:\n%.6f W', avgPower);

            % --- Received Signal (AWGN) ---
            cla(app.AxesFiltered);
            t_rx = (0:length(rxSignal) - 1) / sps;
            plot(app.AxesFiltered, t_rx, rxSignal, 'LineWidth', 1.2, 'Color', [0.12 0.47 0.71]);
            grid(app.AxesFiltered, 'on'); grid(app.AxesFiltered, 'minor');
            title(app.AxesFiltered, sprintf('%s Pulse-Shaped Signal with AWGN (SNR = %d dB)', filterType, SNR_dB));
            xlabel(app.AxesFiltered, 'Time (Bit Periods)'); ylabel(app.AxesFiltered, 'Amplitude (V)');

            % --- PSD Spectrum ---
            cla(app.AxesPSD);
            N = length(rxSignal);
            winLen = min(1024, floor(N / 2));
            if winLen < 16, winLen = N; end
            
            [pxx, f] = pwelch(rxSignal, hanning(winLen), floor(winLen/2), winLen*2, Fs);
            normMag = sqrt(pxx) / max(sqrt(pxx));

            plot(app.AxesPSD, f / Rb, normMag, 'LineWidth', 1.5, 'Color', [0.12 0.47 0.71]);
            grid(app.AxesPSD, 'on');
            title(app.AxesPSD, sprintf('Normalized PSD Spectrum (%s + %s)', lineCode, filterType));
            xlabel(app.AxesPSD, 'Frequency (Normalized to Bit Rate R_b)'); ylabel(app.AxesPSD, 'Normalized Magnitude');
            app.AxesPSD.XLim = [0, 5]; app.AxesPSD.YLim = [0, 1.05];

            % --- Eye Diagram ---
            cla(app.AxesEye);
            hold(app.AxesEye, 'on');
            traceLen = 2 * sps;
            numTraces = floor(length(rxSignal) / traceLen);
            t_trace = (0:traceLen-1) / sps;

            for k = 1:numTraces
                idx = (k-1)*traceLen + (1:traceLen);
                plot(app.AxesEye, t_trace, rxSignal(idx), 'b-', 'LineWidth', 0.5);
            end
            
            hold(app.AxesEye, 'off');
            grid(app.AxesEye, 'on');
            title(app.AxesEye, 'Eye Diagram (2 Symbol Intervals)');
            xlabel(app.AxesEye, 'Time (Symbol Periods)'); ylabel(app.AxesEye, 'Amplitude (V)');
        end
    end
end