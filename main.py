from loader import *
import matplotlib.pyplot as plt
from system_parametrs_settings import *
from func_calculated.msg_to_bits_cipher  import * 
from func_plot.view_bits_cipher import*
from func_calculated.noise_ocean_created import*
from func_plot.view_noise_component import*
from func_calculated.signal_processing import*
from func_plot.view_lfm_with_noise import*

if __name__ == "__main__":
## П.1 Начальные данные
    print('ПУНКТ №1. Очистка данных, подгрузка переменных ')
    print('\n\n')
    clear_console()             # Очистка данных в консоли
    load_modules()              # Инициализация дирикторий программы и соответсвенных исполняемых файлов .py

    params = set_system_parametrs() # Инициализация параметров системы 
    get_system_parameters(params)   # Вывод информации системы

## П.2 Шифрование сообщения
    print('\n\n')
    print("\n" + "="*60)
    print('ПУНКТ №2. Выбор метода шифрования, создание битов')
    print("="*60)
    message, key, bits_per_char, encypt_metod = params['msg'], params['key_bytes'], params['BITS_PER_CHAR'], 'chacha20'
    encrypted = message_to_bits(message, key, bits_per_char, encypt_metod)
    print(f'Результаты шифрования:\n{encrypted}')
    decrypted = bits_to_message(encrypted, key, bits_per_char, encypt_metod)
    print(f'Исходный текст: {message}')
    print(f"Расшифровано: {decrypted}")
    print(f"Результат сравнения исходника и дешифрованного сообщения: {'Совпадает' if message == decrypted else 'Не совпадает'}")

## П.3 Визуализация зашифрованной последовательности битов
    print('\n\n')
    print("\n" + "="*60)
    print('ПУНКТ №3. Визуализация битов')
    print("="*60)
    fig_1_bits_info = plot_bits(
            encrypted,
            "Битовое представление зашифрованного сообщения",
            "blue",
            save = False
        )

    # График сравнения исходых битов с зашифрованнными
    fig_2_bits_origin_and_encypt= plot_comparison(
        message,
        key,
        encypt_metod,
        bits_per_char,
        save = False
    )
    
## П.4 Формирмирование модели шума морской среды
    print('\n\n')
    print("\n" + "="*60)
    print('ПУНКТ №4. Создание шума по модели')
    print("="*60)
    num_bits = len(encrypted)
    print(f'Количетсво отсчетов (num_bits) {num_bits}')
    fs = params['fs']
    T_sym = params['T_sym']
    total_time = num_bits * T_sym 
    total_samples = round(total_time * fs)
    noise_all, _ = generate_ocean_noise(params, num_bits, 'all')
    print(f"Шум сгенерирован")
    print(f"Количество отсчетов: {len(noise_all)}")
    print(f"Длительность: {len(noise_all)/fs:.2f} с")

## П.5 Визуализация данных
    print('\n\n')
    print("\n" + "="*60)
    print('ПУНКТ №5. Визуализация компонентов шума и анализом')
    print("="*60)
    # 5.1 Временная область (с сохранением в папку plots)
    plot_ocean_noise_time(noise_all, fs, save=False, save_dir='output')
    # # 5.2 Фрагмент шума (с сохранением с конкретным именем)
    plot_ocean_noise_fragment(noise_all, fs, n_samples=10000, 
                             save=False, save_dir='output', filename='fragment_noise.png')
    # # 5.3 Гистограмма распределения (без сохранения)
    plot_ocean_noise_histogram(noise_all, save=False)
    # # 5.4 Спектр (с сохранением)
    plot_ocean_noise_spectrum(noise_all, fs, save=False, save_dir='output')
    # # 5.5 Спектрограмма
    plot_ocean_noise_spectrogram(noise_all, fs, save=False, save_dir='output')
    # # 5.6 QQ-plt
    plot_ocean_noise_qq(noise_all, save=False, save_dir='output')
    # # 5.7 Все графики в одном окне (комплексный анализ)
    plot_ocean_noise_all(noise_all, fs, save=False, save_dir='output', 
                       filename='complete_noise_analysis.png')

## П.6. Формирование линейно-частотной модуляции с данными зашифрованными и наложение шума
    print('\n\n')
    print("\n" + "="*60)
    print('ПУНКТ №6. Формирование ЛЧМ и внедрение данных в сигнал ')
    print("="*60)
    # signal, time = generate_lfm(params, encrypted)
    # # noise_all = noise_all[:len(signal)]
    # if len(signal) == len(noise_all):
    #     samples = len(signal)
    # else:
    #     print('Нет совпадения в размерности сигнала и шума')
    # print(f'Размер сигнала : {len(signal)}')
    # print(f'Размер шума    : {len(noise_all)}')
    # #  # Применяем эффекты канала и добавляем шум
    # combinate_signal = combinate_signal_status(params, signal, noise_all, time)

## П.7. Визуализация ЛЧМ с шумом
    print('\n\n')
    print("\n" + "="*60)
    print('ПУНКТ №7. Визуализируем шум и мощность сигнала')
    print("="*60)
#     view_lfm_noise_comparison(
#     signal,
#     noise_all,
#     combinate_signal,
#     n_samples=samples
# )
#     fig = view_power_spectrum(
#     signal,
#     combinate_signal,
#     fs
# )
#     view_spectrogram(
#         noise_all,
#         combinate_signal,
#         fs
# )



# Выводим все графики
    plt.show()
    