import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

st.set_page_config(
    page_title="Line Code Analyzer - SP25",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Line Code Analyzer")
st.caption("SP25 Digital Communication Group Project — MATLAB application converted to Python/Streamlit")

# -----------------------------
# Helper functions
# -----------------------------
def validate_binary(value: str):
    value = value.strip()
    if not value or any(ch not in "01" for ch in value):
        return None
    return np.array([int(ch) for ch in value], dtype=float)


def nrz_encode(bits, sps):
    symbols = 2 * bits - 1
    return np.repeat(symbols, sps)


def rz_encode(bits, sps):
    symbols = 2 * bits - 1
    half = sps // 2
    pulse = np.concatenate([np.ones(half), np.zeros(sps - half)])
    return np.concatenate([symbols[i] * pulse for i in range(len(symbols))])


def manchester_encode(bits, sps):
    symbols = 2 * bits - 1
    half = sps // 2
    pulse = np.concatenate([np.ones(half), -np.ones(sps - half)])
    out = np.concatenate([symbols[i] * pulse for i in range(len(symbols))])

    # Preserve the MATLAB application's convention:
    # bit 0 uses the opposite transition.
    for i, bit in enumerate(bits):
        if bit == 0:
            start = i * sps
            out[start:start + sps] *= -1
    return out


def line_encode(bits, line_code, sps):
    code = line_code.upper()
    if code == "NRZ":
        return nrz_encode(bits, sps)
    if code == "RZ":
        return rz_encode(bits, sps)
    if code == "MANCHESTER":
        return manchester_encode(bits, sps)
    raise ValueError("Unsupported line code")


def gaussian_filter(BT, span, sps):
    # Approximate MATLAB gaussdesign(BT, span, sps)
    # The Gaussian pulse is normalized to unit sum.
    t = np.arange(-span / 2, span / 2 + 1 / sps, 1 / sps)
    # BT is used to control the Gaussian width.
    sigma = np.sqrt(np.log(2)) / (2 * np.pi * max(BT, 1e-6))
    h = np.exp(-0.5 * (t / sigma) ** 2)
    h /= np.sum(h)
    return h


def rrc_filter(rolloff, span, sps):
    # Root-raised-cosine FIR impulse response.
    alpha = float(np.clip(rolloff, 0.0, 1.0))
    t = np.arange(-span / 2, span / 2 + 1 / sps, 1 / sps)
    h = np.zeros_like(t)

    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            h[i] = 1 + alpha * (4 / np.pi - 1)
        elif alpha > 0 and abs(abs(4 * alpha * ti) - 1) < 1e-10:
            h[i] = (
                alpha / np.sqrt(2)
                * (
                    (1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha))
                    + (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha))
                )
            )
        else:
            numerator = (
                np.sin(np.pi * ti * (1 - alpha))
                + 4 * alpha * ti * np.cos(np.pi * ti * (1 + alpha))
            )
            denominator = np.pi * ti * (1 - (4 * alpha * ti) ** 2)
            h[i] = numerator / denominator

    h /= np.sqrt(np.sum(h ** 2))
    return h


def add_awgn(x, snr_db, rng):
    power = np.mean(np.abs(x) ** 2)
    noise_power = power / (10 ** (snr_db / 10))
    noise = rng.normal(0, np.sqrt(noise_power), size=x.shape)
    return x + noise


def normalized_psd(x, fs):
    # Welch PSD, corresponding to the MATLAB pwelch stage.
    n = len(x)
    win_len = min(1024, max(16, n // 2))
    if n < 16:
        win_len = n
    noverlap = win_len // 2
    f, pxx = signal.welch(
        x,
        fs=fs,
        window="hann",
        nperseg=win_len,
        noverlap=min(noverlap, win_len - 1),
        nfft=max(2 * win_len, 32),
        scaling="density",
    )
    mag = np.sqrt(np.maximum(pxx, 0))
    if np.max(mag) > 0:
        mag /= np.max(mag)
    return f, mag


def eye_traces(x, sps):
    trace_len = 2 * sps
    num_traces = len(x) // trace_len
    t = np.arange(trace_len) / sps
    traces = []
    for k in range(num_traces):
        start = k * trace_len
        traces.append(x[start:start + trace_len])
    return t, traces


# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.header("Simulation Controls")

    binary_input = st.text_input(
        "Binary Input",
        value="100101111001",
        help="Enter a sequence containing only 0 and 1.",
    )

    line_code = st.selectbox(
        "Line Code",
        ["Manchester", "NRZ", "RZ"],
        index=0,
    )

    filter_type = st.selectbox(
        "Pulse Shaping",
        ["Gaussian", "RRC", "Rectangular"],
        index=0,
    )

    sps = st.number_input(
        "Samples/Symbol",
        min_value=8,
        max_value=100,
        value=50,
        step=1,
    )

    snr_db = st.number_input(
        "Channel SNR (dB)",
        value=20.0,
        step=1.0,
    )

    bt = st.number_input(
        "Gaussian BT",
        min_value=0.01,
        max_value=2.0,
        value=0.50,
        step=0.05,
    )

    rolloff = st.number_input(
        "RRC Roll-off (α)",
        min_value=0.0,
        max_value=1.0,
        value=0.35,
        step=0.05,
    )

    run = st.button("▶ Run Analysis", use_container_width=True)

# -----------------------------
# Analysis
# -----------------------------
bits = validate_binary(binary_input)

if bits is None:
    st.error("Please provide a valid binary string containing only 0s and 1s.")
    st.stop()

sps = int(sps)
Fs = 48000.0
span = 8
Tb = sps / Fs
Rb = 1 / Tb

# Binary and oversampled representation
oversampled_raw = np.repeat(2 * bits - 1, sps)
t_over = np.arange(len(oversampled_raw)) / sps

# Line coding
line_coded = line_encode(bits, line_code, sps)
t_lc = np.arange(len(line_coded)) / sps

# Filters
sig_rect = line_coded.copy()
h_gauss = gaussian_filter(bt, span, sps)
sig_gauss = signal.fftconvolve(line_coded, h_gauss, mode="same")

h_rrc = rrc_filter(rolloff, span, sps)
sig_rrc = signal.fftconvolve(line_coded, h_rrc, mode="same")

if filter_type == "Rectangular":
    shaped = sig_rect
elif filter_type == "Gaussian":
    shaped = sig_gauss
else:
    shaped = sig_rrc

# Use a deterministic seed so the app is reproducible for the same inputs.
seed = (
    sum((i + 1) * int(b) for i, b in enumerate(binary_input.strip()))
    + int(snr_db * 10)
    + int(sps)
)
rng = np.random.default_rng(seed)
rx_signal = add_awgn(shaped, snr_db, rng)

# Metrics
total_energy = np.sum(np.abs(rx_signal) ** 2) / Fs
avg_power = np.mean(np.abs(rx_signal) ** 2)

# PSD
f, norm_mag = normalized_psd(rx_signal, Fs)

# Eye diagram
t_eye, traces = eye_traces(rx_signal, sps)

# -----------------------------
# Metrics
# -----------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Input Bits", len(bits))
m2.metric("Samples/Symbol", sps)
m3.metric("Total Energy", f"{total_energy:.6e} J")
m4.metric("Average Power", f"{avg_power:.6f} W")

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs([
    "Fig 2: Binary vs Oversampled",
    "Fig 3: Line Code",
    "Fig 4: Filter Comparison",
    "Received (AWGN)",
    "PSD Spectrum",
    "Eye Diagram",
])

with tabs[0]:
    fig, axes = plt.subplots(2, 1, figsize=(11, 7))

    axes[0].stem(
        np.arange(len(bits)),
        bits,
        linefmt="C1-",
        markerfmt="C1o",
        basefmt=" ",
    )
    axes[0].set_title("Figure 2(a): Original Binary Input Sequence")
    axes[0].set_xlabel("Bit Index")
    axes[0].set_ylabel("Logic Level")
    axes[0].set_xlim(-0.5, len(bits) - 0.5)
    axes[0].set_ylim(-0.2, 1.2)
    axes[0].grid(True)

    axes[1].plot(t_over, oversampled_raw, linewidth=1.5)
    axes[1].set_title(f"Figure 2(b): Oversampled Discrete-Time Representation (sps = {sps})")
    axes[1].set_xlabel("Time (Bit Periods)")
    axes[1].set_ylabel("Amplitude (V)")
    axes[1].set_xlim(0, len(bits))
    axes[1].set_ylim(-1.3, 1.3)
    axes[1].grid(True)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with tabs[1]:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(t_lc, line_coded, linewidth=1.5)
    ax.set_title(f"Figure 3: {line_code} Line-Coded Baseband Waveform")
    ax.set_xlabel("Time (Bit Periods)")
    ax.set_ylabel("Amplitude (V)")
    ax.set_ylim(-1.3, 1.3)
    ax.grid(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with tabs[2]:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(t_lc, sig_rect, "--", linewidth=1.2, label="Unfiltered (Rectangular)")
    ax.plot(t_lc, sig_gauss, linewidth=1.6, label=f"Gaussian (BT = {bt:.2f})")
    ax.plot(t_lc, sig_rrc, linewidth=1.6, label=f"RRC (α = {rolloff:.2f})")
    ax.set_title("Figure 4: Effect of Pulse-Shaping Filters on Transmitted Waveform")
    ax.set_xlabel("Time (Bit Periods)")
    ax.set_ylabel("Amplitude (V)")
    ax.set_xlim(0, len(bits))
    ax.grid(True)
    ax.legend(loc="upper right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with tabs[3]:
    t_rx = np.arange(len(rx_signal)) / sps
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(t_rx, rx_signal, linewidth=1.2)
    ax.set_title(f"{filter_type} Pulse-Shaped Signal with AWGN (SNR = {snr_db:g} dB)")
    ax.set_xlabel("Time (Bit Periods)")
    ax.set_ylabel("Amplitude (V)")
    ax.grid(True, which="both")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with tabs[4]:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(f / Rb, norm_mag, linewidth=1.5)
    ax.set_title(f"Normalized PSD Spectrum ({line_code} + {filter_type})")
    ax.set_xlabel("Frequency (Normalized to Bit Rate Rb)")
    ax.set_ylabel("Normalized Magnitude")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.05)
    ax.grid(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with tabs[5]:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for trace in traces:
        ax.plot(t_eye, trace, linewidth=0.5)
    ax.set_title("Eye Diagram (2 Symbol Intervals)")
    ax.set_xlabel("Time (Symbol Periods)")
    ax.set_ylabel("Amplitude (V)")
    ax.grid(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with st.expander("Processing chain"):
    st.write(
        "Binary input → line coding → pulse shaping → AWGN channel → "
        "energy/power calculation → PSD analysis → eye diagram."
    )
    st.write(
        f"**Selected:** {line_code} | {filter_type} | "
        f"{sps} samples/symbol | {snr_db:g} dB SNR | "
        f"BT={bt:.2f} | α={rolloff:.2f}"
    )
