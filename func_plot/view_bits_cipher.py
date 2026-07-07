import numpy as np
import matplotlib.pyplot as plt
from func_calculated.msg_to_bits_cipher import message_to_bits, bits_to_message
import os
from datetime import datetime

def get_output_path(filename):
    """
    Формирует путь для сохранения файла в папке output
    """
    # Определяем корневую директорию проекта (chenel_python_18_06_2026)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(root_dir, 'output')
    
    # Создаем папку output, если её нет
    os.makedirs(output_dir, exist_ok=True)
    
    return os.path.join(output_dir, filename)


def plot_bits(bits_array, title="Битовое представление", color="gray", figsize=(16, 7), save=False):
    """
    Функция для построения графика битов с выделением 0 и 1 кругами
    
    Параметры:
        save: bool - если True, сохраняет график в папку output
    """
    bits_array = np.asarray(bits_array).flatten()
    x = np.arange(len(bits_array))                    
    plt.figure(figsize=figsize)
    # Столбцы (фон)
    plt.bar(x, bits_array, color=color, alpha=0.4, width=0.8)
    # Красные для 1
    plt.scatter(x[bits_array == 1], 
                bits_array[bits_array == 1],
                color='red', s=90, zorder=5, 
                edgecolor='darkred', linewidth=1.5, 
                label='Бит = 1')
    # Синие для 0
    plt.scatter(x[bits_array == 0], 
                bits_array[bits_array == 0],
                color='blue', s=90, zorder=5, 
                edgecolor='darkblue', linewidth=1.5, 
                label='Бит = 0')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Индекс бита')
    plt.ylabel('Значение бита (0/1)')
    # plt.ylim(-0.15, 1.15)
    # plt.xlim(0, 40)
    plt.grid(True, alpha=0.3)
    
    # Статистика
    ones = int(np.sum(bits_array))
    zeros = len(bits_array) - ones
    plt.text(0.02, 0.95, f'Единиц (1): {ones}   Нулей (0): {zeros}   Всего: {len(bits_array)}',
             fontsize=11, backgroundcolor='white', 
             bbox=dict(boxstyle="round,pad=0.5", alpha=0.9))
    
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    # Сохранение графика
    if save:
        # Генерируем имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plot_bits_{timestamp}.png"
        filepath = get_output_path(filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"График сохранён: {filepath}")
    


def plot_comparison(message, key_bytes, encrypt_method, bits_per_char=16, figsize=(16, 7), save=False):
    """
    Сравнивает оригинальное и зашифрованное сообщение на одном графике
    с выделением битов 0 и 1 кружечками
    
    Параметры:
        save: bool - если True, сохраняет график в папку output
    """
    
    # Получаем биты
    original_bits = message_to_bits(message, key_bytes, bits_per_char, 'none')
    encrypted_bits = message_to_bits(message, key_bytes, bits_per_char, encrypt_method)
    
    # Преобразуем в numpy массивы
    original_bits = np.asarray(original_bits).flatten()
    encrypted_bits = np.asarray(encrypted_bits).flatten()
    
    x_orig = np.arange(len(original_bits))
    x_enc = np.arange(len(encrypted_bits))
    
    # Создаём два подграфика
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # ==================== ОРИГИНАЛ ====================
    ax1.bar(x_orig, original_bits, color='green', alpha=0.4, width=0.8)
    
    # Кружечки для оригинала 0 и 1
    ax1.scatter(x_orig[original_bits == 1], original_bits[original_bits == 1],
                color='lime', s=80, zorder=5, edgecolor='darkgreen', linewidth=1.2, label='Бит = 1')
    ax1.scatter(x_orig[original_bits == 0], original_bits[original_bits == 0],
                color='blue', s=80, zorder=5, edgecolor='darkblue', linewidth=1.2, label='Бит = 0')
    
    ax1.set_title('Оригинальное сообщение (без шифрования)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Значение бита')
    # ax1.set_ylim(-0.15, 1.15)
    ax1.set_xlim(0, 50)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    
    # ==================== ЗАШИФРОВАННОЕ ====================
    method_names = {
        'xor': 'XOR',
        'caesar': 'Цезарь',
        'reverse': 'Инверсия',
        'chacha20': 'ChaCha20',
        'none': 'Без шифрования'
    }
    method_display = method_names.get(encrypt_method, encrypt_method.upper())
    
    ax2.bar(x_enc, encrypted_bits, color='red', alpha=0.4, width=0.8)
    
    # Кружечки для зашифрованного
    ax2.scatter(x_enc[encrypted_bits == 1], encrypted_bits[encrypted_bits == 1],
                color='red', s=80, zorder=5, edgecolor='darkred', linewidth=1.2, label='Бит = 1')
    ax2.scatter(x_enc[encrypted_bits == 0], encrypted_bits[encrypted_bits == 0],
                color='blue', s=80, zorder=5, edgecolor='darkblue', linewidth=1.2, label='Бит = 0')
    
    ax2.set_title(f'Зашифрованное сообщение ({method_display})', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Индекс бита')
    ax2.set_ylabel('Значение бита')
    # ax2.set_ylim(-0.15, 1.15)
    ax2.set_xlim(0, 50)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right')
    
    # Общий заголовок
    short_msg = message[:50] + ("..." if len(message) > 50 else "")
    fig.suptitle(f'Сравнение оригинального и зашифрованного сообщения\n"{short_msg}"',
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Статистика
    stats_text = f'Длина оригинала: {len(original_bits)} бит\n' \
                 f'Длина зашифрованного: {len(encrypted_bits)} бит'
    plt.figtext(0.02, 0.02, stats_text, fontsize=11,
                bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))
    
    plt.tight_layout()
    
    # Сохранение графика
    if save:
        # Генерируем имя файла с временной меткой и методом шифрования
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{encrypt_method}_{timestamp}.png"
        filepath = get_output_path(filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"График сохранён: {filepath}")
    
    