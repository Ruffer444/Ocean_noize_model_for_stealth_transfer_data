import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft, fftshift
from scipy.signal import spectrogram

def generate_lfm(params, encrypted):
    """
    Генерация ЛЧМ сигнала для всей битовой последовательности.

    Каждый бит занимает один символ длительностью T_sym.
    На выходе получается один длинный сигнал.
    """

    f_start = params['f_start']
    f_end = params['f_end']
    T_sym = params['T_sym']
    fs = params['fs']
    N_sym = params['N_sym']

    # Время одного символа
    t_symbol = np.linspace(0, T_sym, N_sym, endpoint=False)

    # Скорость изменения частоты
    k = (f_end - f_start) / T_sym

    signal_parts = []

    for bit in encrypted:

        # Базовый ЛЧМ
        phase = 2 * np.pi * (
            f_start * t_symbol +
            0.5 * k * t_symbol**2
        )

        chirp = np.sin(phase)

        # Простая двоичная модуляция:
        # 1 -> обычный сигнал
        # 0 -> инвертированный
        if bit == 0:
            chirp = -chirp

        signal_parts.append(chirp)

    # Склеиваем все символы
    signal = np.concatenate(signal_parts)

    # Временная ось всего сигнала
    time = np.arange(len(signal)) / fs

    print("Чистый ЛЧМ сигнал сформирован")
    print(f"Количество бит: {len(encrypted)}")
    print(f"Отсчетов на символ: {N_sym}")
    print(f"Общее количество отсчетов: {len(signal)}")
    print(f"Длительность: {len(signal)/fs:.3f} сек")

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
    print("\t\tОБРАБОТКА СИГНАЛА В КАНАЛЕ")
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
    print("\n  Добавление шума:")
    if len(noise) != len(processed_signal):
        raise ValueError(
            f"Размеры не совпадают: "
            f"signal={len(processed_signal)}, noise={len(noise)}"
        )
    signal_power = np.mean(processed_signal**2) # мощность сигнала
    snr_linear = 10 ** (params['SNR_target_dB'] / 10) # соотношение из дБ в линейную величину
    noise_power_target = signal_power / snr_linear # какая мощность шума должна быть чтобы достичь требуемого SNR
    noise = noise / np.sqrt(np.mean(noise**2)) # нормируем
    noise = noise * np.sqrt(noise_power_target)

    noisy_signal = processed_signal + noise # Наложение шума и сигнала
    # проверка после масштабирования
    real_snr = 10 * np.log10( 
    np.mean(processed_signal**2) /
    np.mean(noise**2)
    )
    print(f"SNR после масштабирования = {real_snr:.2f} дБ")


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