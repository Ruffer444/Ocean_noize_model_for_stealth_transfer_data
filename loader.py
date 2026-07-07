import sys
import os

def load_modules():
    """Просто загружает модули из папок func_plot и func_print"""
    
    # Добавляем пути к папкам
    sys.path.append('func_plot')
    sys.path.append('func_calculated')
    
    # Импортируем модули
    import func_plot
    import func_calculated
    print('Модули импортированы! Работа программы начинается )))')
    # Возвращаем их, чтобы использовать
    return func_plot, func_calculated

def clear_console():
    "Очистка данных при запуске. "
    os.system('cls' if os.name == 'nt' else 'clear')



