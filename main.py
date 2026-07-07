from loader import *
import matplotlib.pyplot as plt
from system_parametrs_settings import set_system_parametrs, get_system_parameters
from func_calculated.msg_to_bits_cipher  import * 
from func_plot.view_bits_cipher import*
from func_calculated.noise_ocean_created import*
from func_plot.view_noise_component import*
from func_calculated.signal_processing import*

if __name__ == "__main__":
## П.1 Начальные данные
    clear_console()             # Очистка данных в консоли
    load_modules()              # Инициализация дирикторий программы и соответсвенных исполняемых файлов .py

    params = set_system_parametrs() # Инициализация параметров системы 
    get_system_parameters(params)   # Вывод информации системы

## П.2 Шифрование сообщения
    message, key, bits_per_char, encypt_metod = params['msg'], params['key_bytes'], params['BITS_PER_CHAR'], 'chacha20'
    encrypted = message_to_bits(message, key, bits_per_char, encypt_metod)
    print(f'Результаты шифрования:\n{encrypted}')
    decrypted = bits_to_message(encrypted, key, bits_per_char, encypt_metod)
    print(f'Исходный текст: {message}')
    print(f"Расшифровано: {decrypted}")
    print(f"Результат сравнения исходника и дешифрованного сообщения: {'Совпадает' if message == decrypted else 'Не совпадает'}")

## П.3 Визуализация зашифрованной последовательности битов
    # fig_1_bits_info = plot_bits(
    #         encrypted,
    #         "Битовое представление зашифрованного сообщения",
    #         "blue",
    #         (9, 7),
    #         save = False
    #     )

    # # График сравнения исходых битов с зашифрованнными
    # fig_2_bits_origin_and_encypt= plot_comparison(
    #     message,
    #     key,
    #     encypt_metod,
    #     bits_per_char,
    #     (9, 7),
    #     save = False
    # )
    
## П.4 Формирмирование модели шума морской среды
    num_bits = len(params['msg']) * params['BITS_PER_CHAR']
    fs = params['fs']
    T_sym = params['T_sym']
    total_time = num_bits * T_sym * 1.5
    total_samples = round(total_time * fs)
    noise_all, _ = generate_ocean_noise(params, num_bits, 'all')
    print(f"Шум сгенерирован")
    print(f"Количество отсчетов: {len(noise_all)}")
    print(f"Длительность: {len(noise_all)/fs:.2f} с")

## П.5 Визуализация данных
    # 5.1 Временная область (с сохранением в папку plots)
    # plot_ocean_noise_time(noise_all, fs, save=True, save_dir='output')
    # # 5.2 Фрагмент шума (с сохранением с конкретным именем)
    # plot_ocean_noise_fragment(noise_all, fs, n_samples=1000, 
    #                          save=True, save_dir='output', filename='fragment_noise.png')
    # # 5.3 Гистограмма распределения (без сохранения)
    # plot_ocean_noise_histogram(noise_all, save=False)
    # # 5.4 Спектр (с сохранением)
    # plot_ocean_noise_spectrum(noise_all, fs, save=True, save_dir='output')
    # # 5.5 Спектрограмма
    # plot_ocean_noise_spectrogram(noise_all, fs, save=True, save_dir='output')
    # # 5.6 QQ-plt
    # plot_ocean_noise_qq(noise_all, save=True, save_dir='output')
    # # 5.7 Все графики в одном окне (комплексный анализ)
    # plot_ocean_noise_all(noise_all, fs, save=False, save_dir='output', 
    #                    filename='complete_noise_analysis.png')

## П.6. Формирование линейно-частотной модуляции
    signal, time = generate_lfm(params)
    
     # Применяем эффекты канала и добавляем шум
    result = combinate_signal_status(params, signal, noise_all, time)

    # print(signal)
    # print(time)








# Выводим все графики
    plt.show()
    