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
    phase = 2*np.pi * (f_start * time * k *time**2 /2)
    signal = np.sin(phase)

    return signal, time


















