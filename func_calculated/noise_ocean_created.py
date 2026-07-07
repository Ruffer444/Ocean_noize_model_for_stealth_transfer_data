import numpy as np
from scipy.signal import butter, filtfilt

def generate_ocean_noise(params, num_bits, components='all'):
    '''
    Генерация шума морской среды из компонент.
    Возможные вариации генерации шума:
    - 'all' -> все компоненты
    - 'none' -> без шума
    
    - 'turb' -> только турбулентный
    - 'wind' -> только ветровой
    - 'thermal' -> только тепловой
    - 'clicks' -> только импульсные(щелчки)
    
    - 'turb+wind' -> турбулентный + ветровой
    - 'turb+thermal' -> турбулентный + тепловой
    - 'turb+clicks' -> турбулентный + импульсный(щелчки)
    - 'wind+thermal' -> ветровой + тепловой
    - 'wind+clicks' -> ветровой + импульсный(щелчки)
    - 'thermal+clicks' -> тепловой + импульсный(щелчки)
    
    - 'turb+wind+thermal' -> турбулентный + ветровой + тепловой
    - 'turb+wind+clicks' -> турбулентный + ветровой + импульсные
    - 'turb+thermmal+clicks' -> турбулентный + тепловой + импульсные
    - 'wind+thermal+clicks' -> ветровой + тепловой + импульсные
    
    АЛЬТЕРНАТИВНЫЙ ВАРИАНТ ВВОДА:
    - список ['turb', 'wind'] -> любой набор компонентов 
    '''

    fs = params['fs']
    T_sym = params['T_sym']

    total_time = num_bits * T_sym * 1.5
    total_samples = round(total_time * fs)
    np.random.seed(42)

    # Теперь определим компоненты
    match components:
        case 'none':
            return np.zeros(total_samples), total_samples
        case 'all':
            comp_list = ['turb', 'wind', 'thermal', 'clicks']
        case 'turb' | 'wind' | 'thermal' | 'clicks':
            comp_list = [components]
        case str if '+' in components:
            comp_list = components.split('+')
        case list():
            comp_list = components
        case _:
            comp_list = ['turb', 'wind', 'thermal', 'clicks']

    # Инициализация шума
    noise = np.zeros(total_samples)
    
    # Генерация компонентов
    if 'turb' in comp_list:
        x = np.random.randn(total_samples)
        noise_turb = 0.05 * filtfilt([1], [1, -0.99], x)
        noise += noise_turb

    if 'wind' in comp_list:
        # ИСПРАВЛЕНО: делим каждый элемент списка на (fs/2)
        b, a = butter(4, [100 / (fs/2), 1000 / (fs/2)], btype='band')
        noise_wind = 0.1 * filtfilt(b, a, np.random.randn(total_samples))
        noise += noise_wind

    if 'thermal' in comp_list:
        # ИСПРАВЛЕНО: делим каждый элемент списка на (fs/2)
        b, a = butter(4, [1000 / (fs/2), 20000 / (fs/2)], btype='band')
        noise_thermal = 0.15 * filtfilt(b, a, np.random.randn(total_samples))
        noise += noise_thermal

    if 'clicks' in comp_list:
        noise_clicks = np.zeros(total_samples)
        click_dur = round(0.0005 * fs)
        num_clicks = round(total_time * 10)
        for _ in range(num_clicks):
            pos = np.random.randint(0, total_samples - click_dur)
            env = np.exp(-np.arange(click_dur)/(click_dur/5))
            noise_clicks[pos:pos+click_dur] += 0.2 * env * np.random.randn(click_dur)    
        noise += noise_clicks

    # Нормализация
    if np.std(noise) > 0:
        noise = noise / np.std(noise)

    return noise, total_samples