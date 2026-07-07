import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft, fftshift
from scipy.signal import spectrogram

def generate_lfm(params):
    """
    Генерируем ЛЧМ сигнал по параметрам системы
    """
    f_start = params['f_start']
    f_end = params['f_end']
    T_sym = params['T_sym']
    fs = params['fs']
    N_sym = params['N_sym']

    # Время модуляции
    time = np.linspace(0, T_sym, N_sym)
    
    # Скорость смены частоты
    k = (f_end - f_start) / T_sym
    
    # Правильная формула фазы
    phase = 2 * np.pi * (f_start * time + k * time**2 / 2)
    signal = np.sin(phase)
    
    print(f"✓ Чистый ЛЧМ сигнал сгенерирован")
    print(f"  Частоты: {params['f_start']/1000:.1f} - {params['f_end']/1000:.1f} кГц")
    print(f"  Длительность сигнала: {params['T_sym']*1000:.2f} мс")
    print(f"  Количество отсчетов: {N_sym}")
    
    return signal, time


def apply_thorp(signal, params):
    """Затухание по Торпу"""
    if not params['status_attenuation']:
        return signal
    
    f_khz = params['fc'] / 1000
    distance = params['distance_km']

    # Формула Торпа
    alpha = (params['A1'] * f_khz**2 / (params['f1'] + f_khz**2) + 
             params['A2'] * f_khz**2 / (params['f2'] + f_khz**2) + 
             params['A3'] * f_khz**2)
    
    # Затухание в дБ
    attenuation_db = alpha * distance

    # Линейный коэффициент
    attenuation_linear = 10 ** (-attenuation_db / 20)
    
    print(f"  Затухание: {attenuation_db:.2f} дБ")
    print(f"  Коэффициент: {attenuation_linear:.4f}")

    return signal * attenuation_linear


def apply_multipath(signal, params):
    """Применяет многолучевость"""
    if not params['status_multipath']:
        return signal
    
    fs = params['fs']
    delays_ms = params['multipath_delays_ms']
    amps = params['multipath_amps']

    result = np.zeros(len(signal))

    for delay_ms, amp in zip(delays_ms, amps):
        delay_samples = int(delay_ms * fs / 1000)

        if delay_samples == 0:
            result += amp * signal
        else:
            shifted = np.roll(signal, delay_samples)
            shifted[:delay_samples] = 0
            result += amp * shifted
    
    print(f"  Задержки (мс): {delays_ms}")
    print(f"  Амплитуды: {amps}")
    
    return result


def apply_doppler(signal, time, params):
    """Применяет эффект Доплера"""
    if not params['status_doppler']:
        return signal
    
    # Для ЛЧМ доплеровский сдвиг можно оценить как смещение частоты
    doppler_shift = 50  # 50 Гц

    doppler_phase = 2 * np.pi * doppler_shift * time
    signal_complex = signal * np.exp(1j * doppler_phase)
    
    print(f"  Доплеровский сдвиг: {doppler_shift} Гц")

    return np.real(signal_complex)


def combinate_signal_status(params, signal, noise, time):
    """
    Комбинирует сигнал с эффектами канала и шумом
    
    Args:
        params: параметры системы
        signal: чистый сигнал
        noise: шум
        time: временная ось
    
    Returns:
        dict: результаты обработки
    """
    print("\n" + "="*60)
    print("ОБРАБОТКА СИГНАЛА В КАНАЛЕ")
    print("="*60)
    
    # Сохраняем чистый сигнал
    clean_signal = signal.copy()
    
    # Копируем для обработки
    processed_signal = signal.copy()
    applied_effects = []
    
    print("\nПрименяемые эффекты:")
    
    # 1. Многолучевость
    if params['status_multipath']:
        print("\n  ► Многолучевость:")
        processed_signal = apply_multipath(processed_signal, params)
        applied_effects.append('многолучевость')
    else:
        print("\n  ○ Многолучевость: ВЫКЛ")
    
    # 2. Затухание по Торпу
    if params['status_attenuation']:
        print("\n  ► Затухание по Торпу:")
        print(f"    Дистанция: {params['distance_km']} км")
        print(f"    Частота: {params['fc']/1000:.1f} кГц")
        processed_signal = apply_thorp(processed_signal, params)
        applied_effects.append('затухание Торпа')
    else:
        print("\n  ○ Затухание по Торпу: ВЫКЛ")
    
    # 3. Эффект Доплера
    if params['status_doppler']:
        print("\n  ► Эффект Доплера:")
        processed_signal = apply_doppler(processed_signal, time, params)
        applied_effects.append('доплер')
    else:
        print("\n  ○ Эффект Доплера: ВЫКЛ")
    
    # 4. Добавляем шум
    print("\n  ► Добавление шума:")
    noisy_signal = processed_signal + noise
    print(f"    SNR: {params['SNR_target_dB']:.0f} дБ")
    print(f"    Мощность сигнала: {np.mean(processed_signal**2):.6f}")
    print(f"    Мощность шума: {np.mean(noise**2):.6f}")
    print(f"    Отношение: {np.mean(processed_signal**2) / np.mean(noise**2):.2f}")

    return {
        'clean': clean_signal,              # чистый сигнал
        'channel': processed_signal,        # после канала (без шума)
        'noisy': noisy_signal,              # с шумом
        'time': time,
        'fs': params['fs'],
        'params': params,
        'applied_effects': applied_effects
    }