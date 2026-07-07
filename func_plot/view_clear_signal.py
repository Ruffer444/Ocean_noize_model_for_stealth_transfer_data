import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, fftshift
from scipy.signal import spectrogram


def plot_signal_with_effects(result):
    time = result['time'] * 1000  # в мс
    fs = result['fs']
    params = result['params']

    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    # 1. Чистый сигнал
    n_show = min(500, len(time))
    axes[0].plot(time[:n_show], result['clean'][:n_show], 'b-', linewidth=1.5)
    axes[0].set_title('1. Чистый ЛЧМ сигнал', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Амплитуда')
    axes[0].grid(True, alpha=0.3)

    # 2. Сигнал после канала
    axes[1].plot(time[:n_show], result['channel'][:n_show], 'g-', linewidth=1.5)
    # Информация о примененных эффектах
    effects = result['applied_effects']
    title = f'2. Сигнал после канала ({", ".join(effects) if effects else "без эффектов"})'
    axes[1].set_title(title, fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Амплитуда')
    axes[1].grid(True, alpha=0.3)
    # 3. Сигнал с шумом
    axes[2].plot(time[:n_show], result['noisy'][:n_show], 'r-', linewidth=1.5)
    axes[2].set_title(f'3. Сигнал с шумом (SNR = {params["SNR_target_dB"]:.0f} дБ)', 
                     fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Время (мс)')
    axes[2].set_ylabel('Амплитуда')
    axes[2].grid(True, alpha=0.3)

    # 4. Спектры всех сигналов
    spec_clean = np.abs(fftshift(fft(result['clean'])))
    spec_channel = np.abs(fftshift(fft(result['channel'])))
    spec_noisy = np.abs(fftshift(fft(result['noisy'])))
    
    freqs = fftshift(fftfreq(len(result['clean']), 1/fs)) / 1000  # в кГц

    axes[3].plot(freqs, spec_clean, 'b-', label='Чистый', alpha=0.7)
    axes[3].plot(freqs, spec_channel, 'g-', label='После канала', alpha=0.7)
    axes[3].plot(freqs, spec_noisy, 'r-', label='С шумом', alpha=0.7)
    axes[3].set_title('4. Сравнение спектров', fontsize=12, fontweight='bold')
    axes[3].set_xlabel('Частота (кГц)')
    axes[3].set_ylabel('Амплитуда')
    axes[3].grid(True, alpha=0.3)
    axes[3].legend()

        # Ограничиваем частоты
    f_start = params['f_start'] / 1000
    f_end = params['f_end'] / 1000
    margin = (f_end - f_start) * 0.3
    axes[3].set_xlim(f_start - margin, f_end + margin)
    
    plt.tight_layout()