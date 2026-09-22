# Line Code Analyzer

Interactive Python/Streamlit conversion of the SP25 Digital Communication Line Code Analyzer.

## Features

- Binary input validation
- NRZ, RZ and Manchester line coding
- Oversampled waveform visualization
- Gaussian, RRC and rectangular pulse shaping
- AWGN channel simulation with configurable SNR
- Total energy and average power
- Welch PSD spectrum
- Eye diagram
- Interactive controls in a Streamlit web interface

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
Line-Code-Analyzer/
├── app.py
├── requirements.txt
└── README.md
```

The original MATLAB application used MATLAB UI components and signal-processing functions. This version reproduces the application's processing flow in Python/Streamlit for browser-based deployment.
