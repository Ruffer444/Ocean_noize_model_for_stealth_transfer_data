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


