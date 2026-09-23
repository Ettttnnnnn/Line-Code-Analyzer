# Line Code Analyzer

A MATLAB-based interactive application for generating and analyzing NRZ, RZ, and Manchester line-coded signals using rectangular, Gaussian, and root-raised-cosine (RRC) filters.

## How to Run

1. Download or clone this repository.
2. Open **MATLAB**.
3. Make sure `LineCodeAnalyzerApp.m` is in the current MATLAB folder or on the MATLAB path.
4. In the MATLAB Command Window, run:

```matlab
LineCodeAnalyzerApp
```

5. The MATLAB-based interactive application will open.

## Application Features

The application allows the user to:

- Enter a binary input sequence.
- Select **NRZ, RZ, or Manchester** line coding.
- Select **Rectangular, Gaussian, or RRC** pulse shaping.
- Set the number of samples per symbol.
- Set the channel SNR.
- Adjust Gaussian BT and RRC roll-off parameters.
- View the oversampled binary representation.
- View the selected line-coded waveform.
- Compare the effect of different pulse-shaping filters.
- Observe the received signal after AWGN.
- View the normalized PSD spectrum.
- View the eye diagram.
- Display calculated signal energy and average power.

## Requirements

- MATLAB
- Signal Processing Toolbox

## Project

**Line Code Analyzer — SP25 Digital Communication Group Project**

IIT Madras — BS in Electronic Systems
