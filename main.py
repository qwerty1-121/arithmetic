from mpmath import *
from collections import Counter
from math import ceil, floor


def calculate_probabilities(input_data):
    frequency = Counter(input_data)  # подсчет частоты каждого байта
    total_chars = len(input_data)  # общее количество байтов
    probabilities = {char: count / total_chars for char, count in frequency.items()}  # вероятности символов
    return probabilities


def calculate_cumulative_freq(probabilities):
    cumulative_freq = {}  # словарь для кумулятивной частоты
    cumulative_prob = 0.0  # начальное значение кумулятивной вероятности
    for char, probability in probabilities.items():
        cumulative_freq[char] = cumulative_prob
        cumulative_prob += probability  # суммируем вероятности
    return cumulative_freq


def encode_numbers(input_data, probabilities, cumulative_freq):
    # Специальные константы, используемые для определения границ и переходов между состояниями в процессе кодирования
    # данных.
    max_value, third, quarter, half = 4294967295, 3221225472, 1073741824, 2147483648

    # Инициализация результата кодирования и границ.
    encoded_numbers = []
    lower_bound, upper_bound = 0, max_value
    stray_digits = 0  # количество отставшихся цифр

    # Основной цикл, проходящий по каждому символу во входных данных
    for char in input_data:
        range_length = upper_bound - lower_bound + 1  # Вычисляем диапазон значений
        # Обновляем границы для арифметического кодирования в зависимости от входных данных
        lower_bound += ceil(range_length * cumulative_freq[char])
        upper_bound = lower_bound + floor(range_length * probabilities[char])

        # Реализуем основную часть алгоритма арифметического кодирования
        temporary_numbers = []
        while True:
            # Если верхняя граница меньше половины (состояние 1)
            if upper_bound < half:
                temporary_numbers.append(0)
                temporary_numbers.extend([1] * stray_digits)
                stray_digits = 0
            # Если нижняя граница больше или равна половине (состояние 2)
            elif lower_bound >= half:
                temporary_numbers.append(1)
                temporary_numbers.extend([0] * stray_digits)
                stray_digits = 0
                lower_bound -= half
                upper_bound -= half
            # Если нижняя граница больше или равна четверти и верхняя граница меньше трети (состояние 3)
            elif lower_bound >= quarter and upper_bound < third:
                stray_digits += 1
                lower_bound -= quarter
                upper_bound -= quarter
            else:
                break

            # Обрабатываем все временные числа и добавляем их к кодированным числам
            if temporary_numbers:
                encoded_numbers.extend(temporary_numbers)
                temporary_numbers = []

            lower_bound *= 2
            upper_bound = 2 * upper_bound + 1

    # Добавляем оставшиеся биты в конце
    encoded_numbers.extend([0] + [1] * stray_digits if lower_bound < quarter else [1] + [0] * stray_digits)

    # Возвращаем закодированные числа
    return encoded_numbers


# Функция кодирования
def arithmetic_encode(input_data):
    # Вычислить вероятности символов во входной строке
    probabilities = calculate_probabilities(input_data)
    # Вычислить кумулятивные частоты для каждого символа в строке
    cumulative_freq = calculate_cumulative_freq(probabilities)
    # Кодируем данные с помощью вероятностей и кумулятивных частот
    encoded_numbers = encode_numbers(input_data, probabilities, cumulative_freq)
    # Возвращает закодированные данные
    return encoded_numbers


# Функция декодирования, которая применяет арифметическое декодирование
def arithmetic_decode(encoded_data, probabilities, data_length):
    # Инициализация констант и разрядов для работы системы
    precision, max_value, third, quarter, half = 32, 4294967295, 3221225472, 1073741824, 2147483648

    # Создание алфавита из вероятностей
    alphabet = list(probabilities)

    # Постройте список кумулятивных вероятностей
    cumulative_freq = [0]
    for item in probabilities:
        cumulative_freq.append(cumulative_freq[-1] + probabilities[item])
    cumulative_freq.pop()

    # Извлечение вероятностей в виде списка для легкого доступа
    probabilities = list(probabilities.values())

    # Добавления нулей к концу для обеспечения точности
    encoded_data.extend(precision * [0])

    # Создание списка для декодированных символов
    decoded_symbols = data_length * [0]

    # Извлечение начального значения из первых битов данных
    current_value = int(''.join(str(bit) for bit in encoded_data[0:precision]), 2)

    # Текущая позиция в битовых данных после инициалиации
    bit_position = precision
    # установка начальных границ
    lower_bound, upper_bound = 0, max_value

    # индекс для списка декодированных символов
    decoded_position = 0

    while 1:
        # Расчитываем пределы для текущего символа
        range_length = upper_bound - lower_bound + 1
        symbol_index = len(cumulative_freq)
        # Позиция значения в диапазоне
        value = (current_value - lower_bound) / range_length

        # Находим соответствующий символ этому значению
        for index, item in enumerate(cumulative_freq):
            if item >= value:
                symbol_index = index
                break
        symbol_index -= 1
        # Добавляем найденный символ в список декодированных символов
        decoded_symbols[decoded_position] = alphabet[symbol_index]

        # Обновляем границы для декодирования следующего символа
        lower_bound = lower_bound + ceil(cumulative_freq[symbol_index] * range_length)
        upper_bound = lower_bound + floor(probabilities[symbol_index] * range_length)

        # Выполняем нормализацию и масштабирование диапазона и текущего значения
        while True:
            if upper_bound < half:
                pass
            elif lower_bound >= half:
                lower_bound -= half
                upper_bound -= half
                current_value -= half
            elif lower_bound >= quarter and upper_bound < third:
                lower_bound -= quarter
                upper_bound -= quarter
                current_value -= quarter
            else:
                break

            # Масштабируем границы и добавляем новые биты в значения
            lower_bound *= 2
            upper_bound = 2 * upper_bound + 1
            current_value = 2 * current_value + encoded_data[bit_position]

            # Перемещаемся к следующему биту
            bit_position += 1

            # Если все биты прочитаны, останавливаем процесс
            if bit_position == len(encoded_data) + 1:
                break

        # Перемещаемся к следующему символу
        decoded_position += 1

        # Если все символы прочитаны, останавливаем процесс
        if decoded_position == data_length or bit_position == len(encoded_data) + 1:
            break
    # Возвращаем байты декодированных символов
    return bytes(decoded_symbols)


# функция для чтения файла. Возвращает прочитанные данные.
def read_file(filename):
    with open(filename, 'rb') as source_file:
        input_data = source_file.read()
    return input_data


# функция для записи данных в файл.
def write_file(filename, data):
    with open(filename, 'wb') as output_file:
        output_file.write(data)


# функция для кодирования данных и упаковки в формат, подходящий для записи в файл.
def encode_data(input_data):
    # ключи - уникальные элементы input_data, а значения — это количество раз, которое каждый уникальный элемент
    # встретился в input_data
    frequencies = dict(Counter(input_data))
    # арифметическое кодирование входных данных
    encoded_sequence = arithmetic_encode(input_data)
    # арифметически закодированная последовательность преобразуется в строку
    encoded_sequence_str = ''.join(map(str, encoded_sequence))

    # добвляем к строке нули, чтобы её длина была кратна 8, для корректного декодирования
    padding_count = 8 - len(encoded_sequence_str) % 8
    encoded_sequence_str += "0" * padding_count

    # Полная закодированная строка состоит из информации о дополнении и закодированной последовательности
    padding_info = "{0:08b}".format(padding_count)
    padded_encoded_str = padding_info + encoded_sequence_str

    # массив байтов из закодированной строки (байты переводятся из двоичной в десятичную СС)
    output_array = bytearray([int(padded_encoded_str[i:i + 8], 2) for i in range(0, len(padded_encoded_str), 8)])

    # конкатенация нескольких блоков данных в один байтовый массив
    return len(input_data).to_bytes(4, 'little') + (len(frequencies.keys()) - 1).to_bytes(1, 'little') + \
        b''.join(byte_value.to_bytes(1, 'little') + frequency.to_bytes(4, 'little') for byte_value, frequency in
                 frequencies.items()) + \
        bytes(output_array)


# функция для декодирования данных из формата файла обратно в исходные данные
def decode_data(encoded_data):
    # В первых 4 байтах закодирована исходная длина данных. Мы получаем её и используем в дальнейшем
    original_length = int.from_bytes(encoded_data[0:4], 'little')
    # В следующем байте закодировано количество уникальных символов минус один.
    unique_count = encoded_data[4] + 1
    # Значения символов и их частоты хранятся в заголовке, начинающемся с пятого байта.
    header = encoded_data[5: 5 * unique_count + 5]

    byte_frequencies = {}
    # Разбираем заголовок на символы и их частоты
    for i in range(unique_count):
        byte_value = header[i * 5]
        frequency = int.from_bytes(header[i * 5 + 1:i * 5 + 5], 'little')
        byte_frequencies[byte_value] = frequency

    # Исходные вероятности символов в данных, расчитываются на основе частот символов
    probabilities = {char: count / original_length for char, count in byte_frequencies.items()}

    # Извлекаем закодированный текст из данных, убирая заголовок.
    encoded_text = encoded_data[5 * (encoded_data[4] + 1) + 5:]
    # Кодированный текст переводим обратно из байтов в бинарную строку, добавляем ведущие нули там где они были
    # дополнены
    padded_encoded_str = ''.join([bin(byte)[2:].rjust(8, '0') for byte in encoded_text])

    # Получаем количество дополнительных битов из первых восьми бит закодированной последовательности
    padding_count = int(padded_encoded_str[:8], 2)
    # Избавляемся от информации о дополнении (и самого дополнения) в закодированной последовательности
    encoded_sequence = padded_encoded_str[8: -padding_count if padding_count != 0 else None]
    # Возвращаем бинарную строку обратно в виде последовательности целых чисел
    encoded_sequence = [int(bit) for bit in encoded_sequence]

    # Декодируем каждый символ, используя полученные вероятности и исходную длину
    decoded_data = arithmetic_decode(encoded_sequence, probabilities, original_length)

    return decoded_data


# функция, запускающая цикл взаимодействия с пользователем
def main():
    operation = input("Do you want to encode(0) or decode(1) your file: ")
    file_name = input("Enter the file name: ")

    if operation == '0':
        input_data = read_file(file_name)
        encoded_data = encode_data(input_data)
        write_file(f'{file_name}.enc', encoded_data)
    elif operation == '1':
        encoded_data = read_file(file_name)
        decoded_data = decode_data(encoded_data)
        write_file(f'{file_name}.dec', decoded_data)


if __name__ == '__main__':
    main()
