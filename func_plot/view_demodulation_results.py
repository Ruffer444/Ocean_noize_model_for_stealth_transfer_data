import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft


def plot_demodulation_results(
        original_signal,
        received_signal,
        demodulated_bits,
        original_bits,
        params,
        title="Результаты демодуляции"
):

    fs = params['fs']

    fig, axes = plt.subplots(4, 1, figsize=(7, 6))

    # ============================================================
    # 1. Исходный и принятый сигнал
    # ============================================================

    n_samples = min(
        1000,
        len(original_signal),
        len(received_signal)
    )

    axes[0].plot(
        original_signal[:n_samples],
        label='Исходный',
        alpha=0.7
    )

    axes[0].plot(
        received_signal[:n_samples],
        label='Синхронизированный',
        alpha=0.7
    )

    axes[0].set_title(
        'Сигнал (первые отсчёты)'
    )

    axes[0].set_xlabel('Отсчёты')
    axes[0].set_ylabel('Амплитуда')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # ============================================================
    # 2. Спектр принятого сигнала
    # ============================================================

    fft_signal = np.abs(fft(received_signal))

    freqs = np.fft.fftfreq(
        len(received_signal),
        1 / fs
    )

    mask = freqs > 0

    axes[1].plot(
        freqs[mask],
        fft_signal[mask]
    )

    axes[1].set_title(
        'Спектр синхронизированного сигнала'
    )

    axes[1].set_xlabel('Частота (Гц)')
    axes[1].set_ylabel('Амплитуда')

    axes[1].set_xlim(
        0,
        min(30000, fs / 2)
    )

    axes[1].grid(True, alpha=0.3)

    # ============================================================
    # 3. Сравнение битов
    # ============================================================

    axes[2].step(
        range(len(original_bits)),
        original_bits,
        where='post',
        label='Исходные',
        linewidth=2
    )

    axes[2].step(
        range(len(demodulated_bits)),
        demodulated_bits,
        where='post',
        linestyle='--',
        label='Демодулированные',
        linewidth=2
    )

    axes[2].set_title(
        'Сравнение исходных и демодулированных битов'
    )

    axes[2].set_xlabel('Номер бита')
    axes[2].set_ylabel('Значение')

    axes[2].set_ylim([-0.2, 1.2])

    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    # ============================================================
    # 4. Ошибки
    # ============================================================

    compare_length = min(
        len(original_bits),
        len(demodulated_bits)
    )

    errors = [
        1 if original_bits[i] != demodulated_bits[i] else 0
        for i in range(compare_length)
    ]

    axes[3].stem(
        range(len(errors)),
        errors,
        basefmt=' '
    )

    axes[3].set_title(
        'Ошибки демодуляции'
    )

    axes[3].set_xlabel('Номер бита')
    axes[3].set_ylabel('Ошибка')

    axes[3].set_ylim([-0.1, 1.1])

    axes[3].grid(True, alpha=0.3)

    # ============================================================
    # Общий заголовок
    # ============================================================

    fig.suptitle(
        title,
        fontsize=16
    )

    fig.tight_layout()

    return fig