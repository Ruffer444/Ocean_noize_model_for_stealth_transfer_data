import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft, fftshift
from scipy.signal import spectrogram

def generate_lfm(params):
#  Генерируем ЛЧМ сигнал по параметрам системы

    f_start = params['f_start']
    f_end = params['f_end']
    T_sym = params['T_sym']
    fs = params['fs']
    N_sym = params['N_sym']

    # Время модуляции
    time = np.linspace(0, T_sym, N_sym)
    # Скорость смены частоты
    k = (f_end - f_start) / T_sym
    phase = 2*np.pi * (f_start * time * k *time**2 /2)
    signal = np.sin(phase)
    print(f"Чистый ЛЧМ сигнал сгенерирован")
    print(f"  Частоты: {params['f_start']/1000:.1f} - {params['f_end']/1000:.1f} кГц")
    print(f"  Длительность сигнала: {params['T_sym']*1000:.2f} мс")
    return signal, time

## Затухание по Торпу
def apply_thorp(signal, params):
    if not params['status_attenuation']:
        return signal
    
    f_khz = params['fc'] / 1000
    distance = params['distance_km']

    # Фомрула Торпа
    alpha = (params['A1'] * f_khz**2 / (params['f1'] + f_khz**2) + 
             params['A2'] * f_khz**2 / (params['f2'] + f_khz**2) + 
             params['A3'] * f_khz**2)
    # Затухание в дБ
    attenuation_db = alpha * distance

    # Линейные коэффициент
    attenuation_linear = 10**(-attenuation_db / 20)

    return signal * attenuation_linear

def apply_multipath(signal, params):
    if not params['status_multipath']:
        return signal
    
    fs = params['fs']
    delays_ms = params['multipath_delays_ms']
    amps = params['multipath_amps']

    result = np.zeros(len(signal))

    for delay_ms, amp in zip(delay_ms, amps):
        delay_samples = int(delays_ms * fs / 1000)

        if delay_samples == 0:
            result += amp *signal
        else:
            shifted = np.roll(signal, delay_samples)
            shifted[:delay_samples] = 0
            result += amp (shifted)
    return result


def apply_doppler(signal, time, params):
        if not params['status_doppler']:
            return signal
        
        # Для ЛЧМ доплеровский сдвиг можн оценить как смещение частоты
        # (малый сдвиг)
        doppler_shift = 50 # 50 Гц

        # 
        doppler_phase = 2*np.pi *doppler_shift * time
        signal_complex = signal * np.exp(1j * doppler_phase)

        return np.real(signal_complex)


def combinate_signal_status(params, signal, noise):
    signal_clear = signal
    applied_effects = []
    # Многолучевость
    if params['status_multipath']:
        signal = apply_multipath(signal, params)
        applied_effects.append('многолучевость')
        print(f" Многолучевость применена")
        print(f"  Лучей: {len(params['multipath_delays_ms'])}")
    else:
        print(f"○ Многолучевость: ВЫКЛ")
        # 3.2 Затухание по Торпу
    if params['status_attenuation']:
        signal = apply_thorp(signal, params)
        applied_effects.append('затухание Торпа')
        print(f"✓ Затухание по Торпу применено")
        print(f"  Дистанция: {params['distance_km']} км")
        print(f"  Частота: {params['fc']/1000:.1f} кГц")
    else:
        print(f"○ Затухание по Торпу: ВЫКЛ")
    
    # 3.3 Эффект Доплера
    if params['status_doppler']:
        signal = apply_doppler(signal, time, params)
        applied_effects.append('доплер')
        print(f"✓ Эффект Доплера применен")
        print(f"  Сдвиг: 50 Гц")
    else:
        print(f"○ Эффект Доплера: ВЫКЛ")

    noisy_signal = signal + noise

    return {
        'clean': clean_signal,           # чистый сигнал
        'channel': signal,               # после канала (без шума)
        'noisy': noisy_signal,           # с шумом
        'time': time,
        'fs': params['fs'],
        'params': params,
        'applied_effects': applied_effects
    }



