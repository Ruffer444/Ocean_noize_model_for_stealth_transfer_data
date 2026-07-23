import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq
import os

def plot_ocean_noise_time(noise, fs, title="Шум морской среды (временная область)", 
                          figsize=(12, 4), save=False, save_dir='plots', filename=None):
    """
    График шума во временной области
    
    Args:
        noise: массив шума
        fs: частота дискретизации (Гц)
        title: заголовок графика
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    time = np.arange(len(noise)) / fs
    ax.plot(time, noise, color='blue', alpha=0.7, linewidth=0.5)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Время, с')
    ax.set_ylabel('Амплитуда')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, time[-1]])
    
    # Добавляем статистику
    stats_text = (f'Длительность: {time[-1]:.2f} с\n'
                  f'Отсчетов: {len(noise):,}\n'
                  f'Ср. значение: {np.mean(noise):.4f}\n'
                  f'Стд. отклонение: {np.std(noise):.4f}')
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_time.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, ax


def plot_ocean_noise_fragment(noise, fs, n_samples=1000, title="Фрагмент шума", 
                              figsize=(12, 4), save=False, save_dir='plots', filename=None):
    """
    График фрагмента шума для детального просмотра
    
    Args:
        noise: массив шума
        fs: частота дискретизации
        n_samples: количество отсчетов для отображения
        title: заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    n_samples = min(n_samples, len(noise))
    time_fragment = np.arange(n_samples) / fs
    
    ax.plot(time_fragment, noise[:n_samples], color='darkblue', linewidth=0.8)
    ax.set_title(f'{title} (первые {n_samples} отсчетов)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Время, с')
    ax.set_ylabel('Амплитуда')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_fragment.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, ax


def plot_ocean_noise_histogram(noise, title="Гистограмма распределения амплитуд", 
                               figsize=(10, 6), save=False, save_dir='plots', filename=None):
    """
    Гистограмма распределения амплитуд шума
    
    Args:
        noise: массив шума
        title: заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    from scipy.stats import norm
    
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.hist(noise, bins=50, color='green', alpha=0.7, edgecolor='black', density=True)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Амплитуда')
    ax.set_ylabel('Плотность вероятности')
    ax.grid(True, alpha=0.3)
    
    # Добавляем кривую нормального распределения для сравнения
    mu, std = np.mean(noise), np.std(noise)
    x = np.linspace(noise.min(), noise.max(), 100)
    ax.plot(x, norm.pdf(x, mu, std), 'r-', linewidth=2, label='Нормальное распределение')
    ax.legend()
    
    # Добавляем статистику
    from scipy.stats import skew, kurtosis
    stats_text = (f'Среднее: {mu:.4f}\n'
                  f'Стд. отклонение: {std:.4f}\n'
                  f'Асимметрия: {skew(noise):.4f}\n'
                  f'Эксцесс: {kurtosis(noise):.4f}')
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))
    
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_histogram.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, ax


def plot_ocean_noise_spectrum(noise, fs, title="Спектр шума", 
                              figsize=(12, 6), save=False, save_dir='plots', filename=None):
    """
    Спектр мощности шума
    
    Args:
        noise: массив шума
        fs: частота дискретизации
        title: заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Спектр в линейном масштабе
    f, Pxx = signal.periodogram(noise, fs, window='hann', scaling='density')
    ax1.semilogy(f, Pxx, color='purple', linewidth=0.8)
    ax1.set_title('Спектральная плотность мощности', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Частота, Гц')
    ax1.set_ylabel('PSD, В²/Гц')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, fs/2])
    
    # Спектр в логарифмическом масштабе
    ax2.loglog(f[1:], Pxx[1:], color='orange', linewidth=0.8)
    ax2.set_title('Спектр в логарифмическом масштабе', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Частота, Гц (лог. шкала)')
    ax2.set_ylabel('PSD, В²/Гц (лог. шкала)')
    ax2.grid(True, alpha=0.3, which='both')
    ax2.set_xlim([f[1], fs/2])
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_spectrum.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, (ax1, ax2)


def plot_ocean_noise_spectrogram(noise, fs, title="Спектрограмма шума", 
                                 figsize=(12, 6), save=False, save_dir='plots', filename=None):
    """
    Спектрограмма шума
    
    Args:
        noise: массив шума
        fs: частота дискретизации
        title: заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Параметры спектрограммы
    nperseg = min(1024, len(noise) // 4)
    noverlap = nperseg // 2
    
    f, t, Sxx = signal.spectrogram(noise, fs, window='hann', 
                                   nperseg=nperseg, noverlap=noverlap,
                                   scaling='density')
    
    # Отображаем в логарифмическом масштабе
    im = ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Время, с')
    ax.set_ylabel('Частота, Гц')
    ax.grid(True, alpha=0.2)
    ax.set_ylim([0, 2500])
    
    # Добавляем colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Мощность, дБ')
    
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_spectrogram.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, ax


def plot_ocean_noise_qq(noise, title="QQ-plot (проверка нормальности)", 
                        figsize=(10, 6), save=False, save_dir='plots', filename=None):
    """
    QQ-plot для проверки нормальности распределения
    
    Args:
        noise: массив шума
        title: заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    from scipy import stats
    
    fig, ax = plt.subplots(figsize=figsize)
    stats.probplot(noise, dist="norm", plot=ax)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_qq.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, ax

def plot_ocean_noise_components(noise_dict, fs, title="Компоненты шума", 
                                figsize=(15, 10), save=False, save_dir='plots', filename=None):
    """
    Визуализация отдельных компонент шума
    
    Args:
        noise_dict: словарь {название_компоненты: массив_шума}
        fs: частота дискретизации
        title: заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    n_components = len(noise_dict)
    fig, axes = plt.subplots(n_components + 1, 1, figsize=figsize)
    
    # Если одна компонента, axes не список
    if n_components == 1:
        axes = [axes]
    
    # Временная ось
    time = np.arange(len(list(noise_dict.values())[0])) / fs
    
    # Суммарный шум
    total_noise = np.zeros_like(list(noise_dict.values())[0])
    for name, noise in noise_dict.items():
        total_noise += noise
    
    # Отображаем суммарный шум
    axes[0].plot(time, total_noise, color='black', linewidth=0.5, alpha=0.8)
    axes[0].set_title('Суммарный шум (все компоненты)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Амплитуда')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, time[-1]])
    
    # Отображаем каждую компоненту
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    for idx, (name, noise) in enumerate(noise_dict.items()):
        ax = axes[idx + 1]
        color = colors[idx % len(colors)]
        ax.plot(time, noise, color=color, linewidth=0.5, alpha=0.7, label=name)
        ax.set_title(f'Компонента: {name}', fontsize=11)
        ax.set_ylabel('Амплитуда')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, time[-1]])
        ax.legend(loc='upper right')
    
    axes[-1].set_xlabel('Время, с')
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_components.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, axes


def plot_ocean_noise_all(noise, fs, title="Полный анализ шума", 
                         figsize=(14, 10), save=False, save_dir='plots', filename=None):
    """
    Комплексная визуализация шума (все графики в одном окне)
    
    Args:
        noise: массив шума
        fs: частота дискретизации
        title: общий заголовок
        figsize: размер фигуры
        save: сохранять ли график (True/False)
        save_dir: директория для сохранения
        filename: имя файла (если None, генерируется автоматически)
    """
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)
    
    # 1. Временная область
    ax1 = fig.add_subplot(gs[0, :])
    time = np.arange(len(noise)) / fs
    ax1.plot(time, noise, color='blue', alpha=0.7, linewidth=0.5)
    ax1.set_title('Временная область', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Время, с')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, time[-1]])
    
    # 2. Фрагмент
    ax2 = fig.add_subplot(gs[1, 0])
    n_samples = min(1000, len(noise))
    time_fragment = np.arange(n_samples) / fs
    ax2.plot(time_fragment, noise[:n_samples], color='darkblue', linewidth=0.8)
    ax2.set_title('Фрагмент сигнала', fontsize=11)
    ax2.set_xlabel('Время, с')
    ax2.set_ylabel('Амплитуда')
    ax2.grid(True, alpha=0.3)
    
    # 3. Гистограмма
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.hist(noise, bins=50, color='green', alpha=0.7, edgecolor='black', density=True)
    ax3.set_title('Распределение амплитуд', fontsize=11)
    ax3.set_xlabel('Амплитуда')
    ax3.set_ylabel('Плотность вероятности')
    ax3.grid(True, alpha=0.3)
    
    from scipy.stats import norm
    mu, std = np.mean(noise), np.std(noise)
    x = np.linspace(noise.min(), noise.max(), 100)
    ax3.plot(x, norm.pdf(x, mu, std), 'r-', linewidth=2, label='Нормальное распределение')
    ax3.legend()
    
    # 4. Спектр
    ax4 = fig.add_subplot(gs[2, 0])
    f, Pxx = signal.periodogram(noise, fs, window='hann', scaling='density')
    ax4.semilogy(f, Pxx, color='purple', linewidth=0.8)
    ax4.set_title('Спектральная плотность мощности', fontsize=11)
    ax4.set_xlabel('Частота, Гц')
    ax4.set_ylabel('PSD, В²/Гц')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([0, fs/2])
    
    # 5. Спектр в логарифмическом масштабе
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.loglog(f[1:], Pxx[1:], color='orange', linewidth=0.8)
    ax5.set_title('Спектр в логарифмическом масштабе', fontsize=11)
    ax5.set_xlabel('Частота, Гц (лог. шкала)')
    ax5.set_ylabel('PSD, В²/Гц (лог. шкала)')
    ax5.grid(True, alpha=0.3, which='both')
    ax5.set_xlim([f[1], fs/2])
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save:
        if filename is None:
            filename = 'ocean_noise_full_analysis.png'
        save_path = os.path.join(save_dir, filename)
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  График сохранен: {save_path}")
    
    
    return fig, [ax1, ax2, ax3, ax4, ax5]