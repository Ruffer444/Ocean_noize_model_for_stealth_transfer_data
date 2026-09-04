import os
import sys


def clear_console():
    # Очистка консоли
    os.system('cls' if os.name == 'nt' else 'clear')


def load_modules():
    
    # Автоматически импортирует все функции из:
    #     func_calculated/
    #     func_plot/

    # Аналогично ручному:
    #     from module import *
    
    folders = [
        'func_calculated',
        'func_plot'
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Доступ к namespace вызывающего модуля (main.py)
    caller_globals = sys._getframe(1).f_globals

    for folder in folders:

        folder_path = os.path.join(base_dir, folder)

        if not os.path.isdir(folder_path):
            print(f'Х Папка не найдена: {folder}')
            continue

        # Добавляем путь к папке
        if folder_path not in sys.path:
            sys.path.insert(0, folder_path)

        for filename in os.listdir(folder_path):

            if not filename.endswith('.py'):
                continue

            if filename.startswith('_'):
                continue

            module_name = filename[:-3]

            try:

                # Импортируем модуль
                module = __import__(module_name)

                # Аналог from module import *
                for name in dir(module):

                    if not name.startswith('_'):
                        caller_globals[name] = getattr(module, name)

                print(f'+ Загружен: {folder}/{filename}')

            except Exception as error:

                print(f'Х Ошибка: {folder}/{filename}')
                print(f'  {error}')

    print('\n+ Все функции автоматически загружены!')

