import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate, find_peaks, butter, filtfilt
from scipy.fft import fft, fftfreq, ifft
from msg_to_bits_cipher import bits_to_message
from noise_ocean_created import generate_ocean_noise

def matched_filter_demodulate(received_signal, params):
    # Демодуляция ЛЧМ сигнала с помощью согласованного фильтра
    # received_signal: принятый сигнал
    # params: параметры системы
  
    fs = params['fs']
    T_sym = params['T_sym']
    N_sym = params['N_sym']
    f_start = params['f_start']
    f_end = params['f_end']

    # Создаем опорый ЛЧМ сигнал для бита = 1
    t_symbol = np.linspace(0, T_sym, N_sym, endpoint=False)
    k = (f_end - f_start) / T_sym

    phase = 2*np.pi * (f_start * t_symbol + 0.5 * k * t_symbol**2)
    reference_chirp_1 = np.sin(phase) # для бита 1

    reference_chirp_0 = -reference_chirp_1

    # Количесвто бит в сигнале
    total_samples = len(received_signal)
    num_bits = total_samples // N_sym

    demodulated_bits = []
    correlation_values = []

    print("\n" + "="*60)
    print("\t\tДЕМОДУЛЯЦИЯ СИГНАЛА ")

    for i in range(num_bits):
        # Извлекаем сегмент сигнала для текущего бита данных
        start_idx = i * N_sym
        end_idx = start_idx + N_sym
        signal_segment = received_signal[start_idx:end_idx]

        # Вычисляем корреляцию с обоими опорными сигналами
        corr_1 = np.sum(signal_segment * reference_chirp_1) / N_sym
        corr_0 = np.sum(signal_segment * reference_chirp_0) / N_sym

        # Выбираем бит с максимальной корреляцией
        if corr_1 > corr_0:
            demodulated_bits.append(1)
            correlation_values.append(corr_1)

        else:
            demodulated_bits.append(0)
            correlation_values.append(corr_0)

    # Метрики качества
    metrics = {
        'correlation_values': correlation_values,
        'avg_correlation': np.mean(correlation_values),
        'min_correlation': np.min(correlation_values),
        'max_correlation': np.max(correlation_values)
    }

    print(f" Демодулировано бит: {len(demodulated_bits)}")
    print(f" Средняя корреляция: {metrics['avg_correlation']:.4f}")
    print(f" Мин. корреляция: {metrics['min_correlation']:.4f}")
    print(f" Макс. корреляция: {metrics['max_correlation']:.4f}")

    return demodulated_bits, metrics

def fft_demodulate(received_signal, params):
    """
    Демодуляция с помощью FFT анализа частоты
    
    Args:
        received_signal: принятый сигнал
        params: параметры системы
    
    Returns:
        tuple: (демодулированные биты, частоты)
    """
    fs = params['fs']
    T_sym = params['T_sym']
    N_sym = params['N_sym']
    
    total_samples = len(received_signal)
    num_bits = total_samples // N_sym
    
    demodulated_bits = []
    dominant_freqs = []
    
    print("\n" + "="*60)
    print("\t\tДЕМОДУЛЯЦИЯ ЧЕРЕЗ FFT")
    print("="*60)
    
    for i in range(num_bits):
        start_idx = i * N_sym
        end_idx = start_idx + N_sym
        signal_segment = received_signal[start_idx:end_idx]
        
        # FFT сегмента
        fft_segment = fft(signal_segment)
        freqs = fftfreq(N_sym, 1/fs)
        
        # Находим доминирующую частоту
        magnitude = np.abs(fft_segment[:N_sym//2])
        dominant_freq_idx = np.argmax(magnitude)
        dominant_freq = freqs[dominant_freq_idx]
        
        # Если доминирующая частота в первой половине диапазона -> бит 1
        # Иначе -> бит 0 (или наоборот, зависит от реализации)
        f_center = (params['f_start'] + params['f_end']) / 2
        
        if dominant_freq < f_center:
            demodulated_bits.append(1)
        else:
            demodulated_bits.append(0)
        
        dominant_freqs.append(dominant_freq)
    
    print(f"  Демодулировано бит: {len(demodulated_bits)}")
    print(f"  Средняя частота: {np.mean(dominant_freqs):.1f} Гц")
    
    return demodulated_bits, dominant_freqs

def envelope_demodulate(received_signal, params):
    """
    Демодуляция через огибающую сигнала
    
    Args:
        received_signal: принятый сигнал
        params: параметры системы
    
    Returns:
        tuple: (демодулированные биты, огибающие)
    """
    fs = params['fs']
    N_sym = params['N_sym']
    
    total_samples = len(received_signal)
    num_bits = total_samples // N_sym
    
    demodulated_bits = []
    envelope_values = []
    
    print("\n" + "="*60)
    print("\t\tДЕМОДУЛЯЦИЯ ЧЕРЕЗ ОГИБАЮЩУЮ")
    print("="*60)
    
    # Вычисляем аналитический сигнал для получения огибающей
    from scipy.signal import hilbert
    analytic_signal = hilbert(received_signal)
    envelope = np.abs(analytic_signal)
    
    for i in range(num_bits):
        start_idx = i * N_sym
        end_idx = start_idx + N_sym
        
        envelope_segment = envelope[start_idx:end_idx]
        
        # Средняя энергия в сегменте
        energy = np.mean(envelope_segment**2)
        
        # Порог для определения бита
        threshold = np.median(envelope)
        
        if energy > threshold:
            demodulated_bits.append(1)
        else:
            demodulated_bits.append(0)
        
        envelope_values.append(energy)
    
    print(f"  Демодулировано бит: {len(demodulated_bits)}")
    
    return demodulated_bits, envelope_values

def calculate_ber(original_bits, demodulated_bits):
    """
    Расчет битовой ошибки (BER)
    
    Args:
        original_bits: исходные биты
        demodulated_bits: демодулированные биты
    
    Returns:
        float: BER (bit error rate)
    """
    if len(original_bits) != len(demodulated_bits):
        print(f"  ВНИМАНИЕ: Разное количество бит!")
        print(f"  Исходных: {len(original_bits)}, Демодулированных: {len(demodulated_bits)}")
        # Обрезаем до минимальной длины
        min_len = min(len(original_bits), len(demodulated_bits))
        original_bits = original_bits[:min_len]
        demodulated_bits = demodulated_bits[:min_len]
    
    errors = sum(1 for i in range(len(original_bits)) 
                 if original_bits[i] != demodulated_bits[i])
    
    ber = errors / len(original_bits) if len(original_bits) > 0 else 1.0
    
    print(f"\n" + "="*60)
    print(f"\t\tРЕЗУЛЬТАТЫ ДЕМОДУЛЯЦИИ")
    print("="*60)
    print(f"  Количество ошибок: {errors}")
    print(f"  BER: {ber:.6f} ({ber*100:.2f}%)")
    print(f"  Правильных бит: {len(original_bits) - errors}/{len(original_bits)}")
    
    return ber


def bit_synchronization(received_signal, params):
    """
    Синхронизация битов — поиск оптимального смещения
    по модулю корреляции с опорным ЛЧМ.
    """

    fs = params['fs']
    N_sym = params['N_sym']
    f_start = params['f_start']
    f_end = params['f_end']
    T_sym = params['T_sym']

    # Опорный ЛЧМ
    t_symbol = np.linspace(
        0,
        T_sym,
        N_sym,
        endpoint=False
    )

    k = (f_end - f_start) / T_sym

    phase = 2 * np.pi * (
        f_start * t_symbol +
        0.5 * k * t_symbol**2
    )

    reference_chirp = np.sin(phase)

    # Поиск оптимального смещения
    best_offset = 0
    best_correlation = -np.inf

    for offset in range(N_sym):

        if offset + N_sym > len(received_signal):
            break

        segment = received_signal[
            offset:offset + N_sym
        ]

        # Корреляция
        correlation = (
            np.sum(segment * reference_chirp)
            / N_sym
        )

        # Используем модуль, потому что
        # бит 0 передается инвертированным ЛЧМ
        correlation_abs = abs(correlation)

        if correlation_abs > best_correlation:
            best_correlation = correlation_abs
            best_offset = offset

    print("\n" + "=" * 60)
    print("\t\tСИНХРОНИЗАЦИЯ")
    print("=" * 60)

    print(
        f"  Оптимальное смещение: "
        f"{best_offset} отсчетов "
        f"({best_offset / fs:.6f} сек)"
    )

    print(
        f"  Максимальная корреляция: "
        f"{best_correlation:.4f}"
    )

    # Обрезаем сигнал
    synchronized_signal = received_signal[best_offset:]

    return synchronized_signal, best_offset



