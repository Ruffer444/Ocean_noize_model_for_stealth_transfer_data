import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import spectrogram, welch
def view_lfm_noise_comparison(signal, noise, result, n_samples=None):
    """
    Визуализация сигнала, шума и их суммы.
    """

    n = min(n_samples, len(signal), len(noise))

    plt.figure(figsize=(12, 5))

    plt.plot(result["noisy"][:n], label="Сигнал + шум", linewidth=1.5, color='red')
    
    plt.plot(noise[:n], label="Шум", alpha=0.7, color='blue')
    # plt.plot(signal[:n], label="ЛЧМ сигнал", linewidth=2, color='blue',linestyle='--')

    plt.title("Наложение ЛЧМ сигнала и шума")
    plt.xlabel("Отсчет")
    plt.ylabel("Амплитуда")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

def view_power_spectrum(signal, result, fs):
    """
    Спектр мощности сигнала и сигнала с шумом.
    """

    noisy_signal = result["noisy"]

    # Спектральная плотность мощности
    f_sig, psd_sig = welch(
        signal,
        fs=fs,
        nperseg=2048
    )

    f_noise, psd_noise = welch(
        noisy_signal,
        fs=fs,
        nperseg=2048
    )

    plt.figure(figsize=(10, 5))

    plt.semilogy(
        f_sig,
        psd_sig,
        label="ЛЧМ сигнал",
        linewidth=2
    )

    plt.semilogy(
        f_noise,
        psd_noise,
        label="ЛЧМ + шум",
        linewidth=2
    )

    plt.title("Спектральная плотность мощности")
    plt.xlabel("Частота, Гц")
    plt.ylabel("Мощность")
    plt.grid(True)
    plt.legend()

def view_spectrogram(noise, result, fs):
    """
    Спектрограммы:
    1) Шум
    2) Сигнал + шум
    """

    noisy_signal = result["noisy"]

    # Спектрограмма шума
    f1, t1, Sxx1 = spectrogram(
        noise,
        fs=fs,
        nperseg=512,
        noverlap=256
    )

    # Спектрограмма смеси
    f2, t2, Sxx2 = spectrogram(
        noisy_signal,
        fs=fs,
        nperseg=512,
        noverlap=256
    )

    fig, ax = plt.subplots(1, 2, figsize=(10, 8))

    # -------------------- Шум --------------------
    pcm1 = ax[0].pcolormesh(
        t1,
        f1,
        10 * np.log10(Sxx1 + 1e-20),
        shading="gouraud"
    )

    ax[0].set_title("Спектрограмма шума")
    ax[0].set_xlabel("Время, с")
    ax[0].set_ylabel("Частота, Гц")
    fig.colorbar(pcm1, ax=ax[0], label="Мощность, дБ")

    # ---------------- Сигнал + шум ----------------
    pcm2 = ax[1].pcolormesh(
        t2,
        f2,
        10 * np.log10(Sxx2 + 1e-20),
        shading="gouraud"
    )

    ax[1].set_title("Спектрограмма сигнала с шумом")
    ax[1].set_xlabel("Время, с")
    ax[1].set_ylabel("Частота, Гц")
    fig.colorbar(pcm2, ax=ax[1], label="Мощность, дБ")

    plt.tight_layout()

    return fig

  