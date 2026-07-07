import secrets
import math
def set_system_parametrs():
    "Все параметры системы размещенны в этом файле."

    ################## ПАРАМЕТРЫ СИГНАЛА #################
    params = {}
    params['fc'] = 1000        # Центральная частота (Гц)
    params['bandwidth'] = 3150 # Полоса сигнала (Гц)
    params['T_sym'] = 0.0075   # Длительность символа (с)
    params['fs'] = 100000      # Частота дискретизации (Гц)
    print('Параметры сигнала загружены (+) ')
   
    ################# ПАРАМЕТРЫ РАСЧЕТА ##################
    params['f_start'] = params['fc'] - params['bandwidth']/2
    params['f_end'] = params['fc'] + params['bandwidth']/2
    params['B'] = params['bandwidth'] * params['T_sym']   # База сигнала
    params['N_sym'] = round(params['T_sym']*params['fs']) # Отсчетов на символ
    params['cp_length'] = round(0.1 * params['N_sym'])    #Циклический префикс
    print('Параметры для расчета загружены (+) ')
    
    ################ Параметры сообщения #################
    params['msg'] = 'Сигнал принят. Обработка звершена!'
    params['BITS_PER_CHAR'] = 16
    params['VERBOSE_MODE'] = 'full' # можно еще compact или конкретное значение символов
    print('Параметры содержания сообщения загружены (+) ')

    ################ КЛЮЧ доступа к шифру ################
    KEY_LENGTH_BYTES = 32 # 32 байта = 256 бит
    params['key_bytes'] =  secrets.token_bytes(KEY_LENGTH_BYTES)
    print('Ключ доступа сгенерирован (+) ')
    
    # если нужна будет строка то лучше так:
    # params['key_str'] = ''.join(f'{b:08b}' for b in params['key_bytes'])

    ############ ПАРАМЕТРЫ АКУСТИЧЕСКОГО КАНАЛА ##########
    params['distance_km'] = 0.2          # Дистанция (км)
    params['status_attenuation'] = False # вкл. или выкл. частотное затухание
    params['status_multipath'] = False # вкл. или выкл. многолучевости
    params['status_doppler'] = False # вкл. или выкл. эффект Доплера
    
    # Коэффициенты для формулы Торпа (затухание в морской воде)
    params['A1'] = 0.109    # Борная кислота
    params['f1'] = 1        # Релаксационная частота борной кислоты (кГц^2)    
    params['A2'] = 40.7     # Сульфат магнийя
    params['f2'] = 4100     # Релаксационная частота сульфата магния (кГц^2)
    params['A3'] = 3.01e-4  # Вязкость чистой воды

    # Параметры многолучевости
    params['multipath_delays_ms'] = [0, 1.5, 3.2, 5.0, 7.5] # Задержки в мс
    params['multipath_amps'] = [1.0, 0.7, 0.4, 0.25, 0.15]  # Относительные амплитуды
    
    # Целевая мощность шума (Параметры шума)
    params['SNR_target_dB'] = -20       # Целевое отношение сигнал/шум (дБ)
    params['rng_seed'] = 42             # seed для шума


    return params

def get_system_parameters(params):
    """Выводит информацию о всех параметрах системы"""
    print('''
            ⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣶⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
            ⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣄⣀⡀⣠⣾⡇⠀⠀⠀⠀ 
            ⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀ 
            ⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⢿⣿⣿⡇⠀⠀⠀⠀ 
            ⠀⣶⣿⣦⣜⣿⣿⣿⡟⠻⣿⣿⣿⣿⣿⣿⣿⡿⢿⡏⣴⣺⣦⣙⣿⣷⣄⠀⠀⠀ 
            ⠀⣯⡇⣻⣿⣿⣿⣿⣷⣾⣿⣬⣥⣭⣽⣿⣿⣧⣼⡇⣯⣇⣹⣿⣿⣿⣿⣧⠀⠀ 
            ⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠸⣿⣿⣿⣿⣿⣿⣿⣷''')
    print("\n                  ПАРАМЕТРЫ СИСТЕМЫ")
    
    print("1) Параметры ЛЧМ сигнала: ")
    print(f"    Центральная частота: {params['fc']/1000:.1f} кГц")
    print(f"    Полоса частот: {params['f_start']/1000:.1f} - {params['f_end']/1000:.1f} кГц")
    print(f"    Длительность символа: {params['T_sym']*1000:.1f} мс")
    print(f"    База сигнала B = {params['B']:.1f} (выигрыш {10*math.log10(params['B']):.1f} дБ)")

    print("2) Параметры акустического канала (Торп): ")
    print(f"    Дистанция: {params['distance_km']:.1f} км")
    print(f"    Многолучевость: {'ВКЛ' if params['status_multipath'] else 'ВЫКЛ'}")
    print(f"    Частотное затухание: {'ВКЛ' if params['status_attenuation'] else 'ВЫКЛ'}")
    print(f"    Эффект Доплера: {'ВКЛ' if params['status_doppler'] else 'ВЫКЛ'}")
    
    print("\n3) Сила сигнала по отношению к шуму:")
    print(f"    Целевой SNR: {params['SNR_target_dB']:.0f} дБ")
    print(f"    Сигнал слабее шума в {10**(-params['SNR_target_dB']/10):.0f} раз по мощности")
    
    print("\n4) Параметры сообщения:")
    print(f"    Сообщение: {params['msg']}")
    print(f"    Бит на символ: {params['BITS_PER_CHAR']}")
    print(f"    Режим вывода: {params['VERBOSE_MODE']}")
    
    print("\n5) Данные о шифровании:")
    # Создаем строку ключа на лету, если её нет
    key_str = ''.join(f'{b:08b}' for b in params['key_bytes'])
    key_display = key_str[:20] + "..." if len(key_str) > 20 else key_str
    print(f"    Ключ (первые 20 бит): {key_display}")
    print(f"    Ключ (полностью): {key_str}")
    print(f"    Длина ключа: {len(params['key_bytes'])} байт")
    
    print("\n6) Параметры многолучевости сигнала:")
    print(f"    Задержки (мс): {params['multipath_delays_ms']}")
    print(f"    Амплитуды: {[round(amp, 2) for amp in params['multipath_amps']]}")
    
    print("\n7) Параметры визуализации:")
    print(f"    Seed для RNG: {params['rng_seed']}")
    print(f"    Частота дискретизации: {params['fs']} Гц")
    print(f"    Отсчетов на символ: {params['N_sym']}")
    print(f"    Длина циклического префикса: {params['cp_length']}")