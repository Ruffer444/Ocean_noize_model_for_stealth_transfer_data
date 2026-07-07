import numpy as np
# Импортируем ChaCha20 из библиотеки pycryptodome
from Crypto.Cipher import ChaCha20
def message_to_bits(message, key_bytes, bits_per_char, encrypt_method):
    """
    Преобразует сообщение в зашифрованный numpy массив битов
    
    Args:
        message: строка для шифрования
        key_bytes: ключ шифрования (байты)
        bits_per_char: количество бит на символ (по умолчанию 16)
        encrypt_method: метод шифрования данных
    Returns:
        numpy.ndarray: зашифрованный массив битов (0 и 1)
    """
    # 1. Сначала переведем сообщение в биты
    bits = []
    for char in message:
        unicode_code = ord(char)    # Представляем символ в его числовой код по табилце UNICODE
        binary_str = format(unicode_code, f'0{bits_per_char}b') # Делаем двоичный код и дополняем слева нулями до 16 знаков
        bits.extend([int(bit) for bit in binary_str]) # Из строки битов делаем список чисел

    # 2. Теперь биты переведем в байты
    if len(bits) % 8 != 0:              # Проверка деления бит на 8 без остатска (для лишних битов)
        bits.extend([0] * (8 - len(bits) % 8)) # Добавляем нули чтобы днила стала кратной 8-ми

    message_bytes = bytearray()         # Пустой массив для хранения чисел от 0 - 255
    for i in range(0, len(bits), 8):    # Цикл идет по значениям кратным 8 т.е. (от 0,8,16,24,...)
        byte_val = 0
        for j in range(8):              # Цикл для сбора 1 байта из 8 бит
            byte_val = (byte_val << 1) | bits[i + j] # Сбор байта бит за битом
        message_bytes.append(byte_val)  # добавляем байт в массив

    # 3. Теперь выбираем метод шифрования
    match encrypt_method: # метод исключающего ИЛИ
        case 'xor':
            key_length = len(key_bytes) #  Определяем длину ключа
            encrypted_bytes = bytearray()  # Пустой массив для переноса данных
            for i in range(len(message_bytes)):  # Для каждого бита сообщени
                key_byte = key_bytes[i % key_length] # Зацикливаине кдюча в случае если он меньше сообщения
                encrypted_bytes.append(message_bytes[i] ^ key_byte) # XOR между байтами сообщения и ключа

        case 'caesar':  # метод Цезаря
            shift = key_bytes[0] % 256 if key_bytes else 1 # первый байт ключа как величина сдвига(0-255)
            print(f'Величина сдвига = {shift}')
            encrypted_bytes = bytearray()  
            for byte in message_bytes:
                encrypted_bytes.append((byte + shift) % 256) # к каждому байюту +сдвиг и делаем проверку чтобы не выйти за 255

        case 'reverse': # Битовая инверсия
            encrypted_bytes = bytearray()
            for byte in message_bytes:
                encrypted_bytes.append(~byte & 0xFF) #делаем побитовое НЕ, оставляя только 8 мл. бит (0-255 диапазон)

        case 'chacha20':
            # Ключ должен быть ровно 32 байта. Если ваш ключ длиннее или короче, это может вызвать ошибку.
            key = key_bytes
            # Создаём шифр с автоматической генерацией случайного nonce (8 байт)
            cipher = ChaCha20.new(key=key)
            # Сохраняем nonce, чтобы потом расшифровать
            #self._chacha_nonce = cipher.nonce  # сохраняем nonce в объекте
            # Шифруем байты сообщения
            encrypted_bytes = bytearray(cipher.encrypt(bytes(message_bytes)))
            # Добавляем nonce в начало зашифрованных данных, чтобы сохранить его для расшифровки
            encrypted_bytes = bytearray(cipher.nonce) + encrypted_bytes

        case 'none':
            # Без шифрования
            encrypted_bytes = message_bytes
        
        case _:
            # Неизвестный метод
            raise ValueError(f"Неизвестный метод: {encrypt_method}. \n Доступны: xor, caesar, reverse, none")

    # теперь надо обратно зашифрованные байты перевести в биты
    encrypted_bits = []
    for byte in encrypted_bytes:
        for j in range(7, -1, -1):
            encrypted_bits.append((byte >> j) & 1)
    
    return np.array(encrypted_bits, dtype=np.int8)


def bits_to_message(encrypted_bits, key_bytes, bits_per_char, encrypt_method):
    """
    Расшифровывает numpy массив битов обратно в сообщение
    """
    # 1. биты в байты
    bits_list = encrypted_bits.tolist() if isinstance(encrypted_bits, np.ndarray) else list(encrypted_bits)
    
    if len(bits_list) % 8 != 0:
        bits_list.extend([0] * (8 - len(bits_list) % 8))
    
    encrypted_bytes = bytearray()
    for i in range(0, len(bits_list), 8):
        byte_val = 0
        for j in range(8):
            byte_val = (byte_val << 1) | bits_list[i + j]
        encrypted_bytes.append(byte_val)
    
    # 2. выбор метода расшифровки через match/case
    match encrypt_method:
        case 'xor':
            # XOR расшифровка (та же операция)
            key_length = len(key_bytes)
            decrypted_bytes = bytearray()
            for i in range(len(encrypted_bytes)):
                key_byte = key_bytes[i % key_length]
                decrypted_bytes.append(encrypted_bytes[i] ^ key_byte)
        
        case 'caesar': #(при дешефровке просто вычитаем сдвиг)
            # Цезарь расшифровка (обратный сдвиг)
            shift = key_bytes[0] % 256 if key_bytes else 1
            decrypted_bytes = bytearray()
            for byte in encrypted_bytes:
                decrypted_bytes.append((byte - shift) % 256)
        
        case 'reverse':
            # Инверсия битов (аналогично шифру)
            decrypted_bytes = bytearray()
            for byte in encrypted_bytes:
                decrypted_bytes.append(~byte & 0xFF)
        
        case 'chacha20':
            key = key_bytes[:32]
            # Первые 8 байт зашифрованного сообщения — это наш nonce
            nonce = bytes(encrypted_bytes[:8])
            # Остальное — сами зашифрованные данные
            ciphertext = bytes(encrypted_bytes[8:])
            # Расшифровываем
            cipher = ChaCha20.new(key=key, nonce=nonce)
            decrypted_bytes = bytearray(cipher.decrypt(ciphertext))
        case 'none':
            # Без шифрования
            decrypted_bytes = encrypted_bytes
        
        case _:
            raise ValueError(f"Неизвестный метод: {encrypt_method}. Доступны: xor, caesar, reverse, none")
    
    # ШАГ 3: байты в биты
    decrypted_bits = []
    for byte in decrypted_bytes:
        for j in range(7, -1, -1):
            decrypted_bits.append((byte >> j) & 1)
    
    # ШАГ 4: биты в сообщение
    total_bits = len(decrypted_bits)
    while total_bits % bits_per_char != 0:
        total_bits -= 1
    
    message_chars = []
    for i in range(0, total_bits, bits_per_char):
        char_bits = 0
        for j in range(bits_per_char):
            if i + j < len(decrypted_bits):
                char_bits = (char_bits << 1) | decrypted_bits[i + j]
        message_chars.append(chr(char_bits))
    
    return ''.join(message_chars) #Склеиваем все символы из списка в одну строку и возвращаем