import cv2
import numpy as np
from music21 import stream, note, chord, meter, key
from collections import OrderedDict

# словарь для перевода гитарных нот в фортепианные (16 ладов)
guitar_to_piano = {
    (1, 0): 'E4', (1, 1): 'F4', (1, 2): 'F#4', (1, 3): 'G4', (1, 4): 'G#4', (1, 5): 'A4',
    (1, 6): 'A#4', (1, 7): 'B4', (1, 8): 'C5', (1, 9): 'C#5', (1, 10): 'D5', (1, 11): 'D#5',
    (1, 12): 'E5', (1, 13): 'F5', (1, 14): 'F#5', (1, 15): 'G5', (1, 16): 'G#5',
    (2, 0): 'B3', (2, 1): 'C4', (2, 2): 'C#4', (2, 3): 'D4', (2, 4): 'D#4', (2, 5): 'E4',
    (2, 6): 'F4', (2, 7): 'F#4', (2, 8): 'G4', (2, 9): 'G#4', (2, 10): 'A4', (2, 11): 'A#4',
    (2, 12): 'B4', (2, 13): 'C5', (2, 14): 'C#5', (2, 15): 'D5', (2, 16): 'D#5',
    (3, 0): 'G3', (3, 1): 'G#3', (3, 2): 'A3', (3, 3): 'A#3', (3, 4): 'B3', (3, 5): 'C4',
    (3, 6): 'C#4', (3, 7): 'D4', (3, 8): 'D#4', (3, 9): 'E4', (3, 10): 'F4', (3, 11): 'F#4',
    (3, 12): 'G4', (3, 13): 'G#4', (3, 14): 'A4', (3, 15): 'A#4', (3, 16): 'B4',
    (4, 0): 'D3', (4, 1): 'D#3', (4, 2): 'E3', (4, 3): 'F3', (4, 4): 'F#3', (4, 5): 'G3',
    (4, 6): 'G#3', (4, 7): 'A3', (4, 8): 'A#3', (4, 9): 'B3', (4, 10): 'C4', (4, 11): 'C#4',
    (4, 12): 'D4', (4, 13): 'D#4', (4, 14): 'E4', (4, 15): 'F4', (4, 16): 'F#4',
    (5, 0): 'A2', (5, 1): 'A#2', (5, 2): 'B2', (5, 3): 'C3', (5, 4): 'C#3', (5, 5): 'D3',
    (5, 6): 'D#3', (5, 7): 'E3', (5, 8): 'F3', (5, 9): 'F#3', (5, 10): 'G3', (5, 11): 'G#3',
    (5, 12): 'A3', (5, 13): 'A#3', (5, 14): 'B3', (5, 15): 'C4', (5, 16): 'C#4',
    (6, 0): 'E2', (6, 1): 'F2', (6, 2): 'F#2', (6, 3): 'G2', (6, 4): 'G#2', (6, 5): 'A2',
    (6, 6): 'A#2', (6, 7): 'B2', (6, 8): 'C3', (6, 9): 'C#3', (6, 10): 'D3', (6, 11): 'D#3',
    (6, 12): 'E3', (6, 13): 'F3', (6, 14): 'F#3', (6, 15): 'G3', (6, 16): 'G#3'
}


def load_templates():
    """Загрузка шаблонов цифр 0-9"""
    templates = {}
    for i in range(11):
        template = cv2.imread(f'digit_{i}.png', 0)  # шаблоны цифр
        if template is not None:
            templates[str(i)] = template
    return templates


def find_digits(image_path, templates):
    """Поиск цифр на изображении"""
    img = cv2.imread(image_path)
    if img is None:
        print("Ошибка загрузки изображения")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # находим контуры
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    digits_info = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # фильтрация размеров
        if w < 2 or h < 2 or w > 200 or h > 100:
            continue

        # Область с цифрой
        digit_roi = binary[y:y + h, x:x + w]

        best_match = None
        best_score = -1

        # сравниваем с каждым шаблоном
        for digit, template in templates.items():
            # масштабируем шаблон под размер найденной области
            resized_template = cv2.resize(template, (w, h))

            # равниваем с помощью корреляции
            result = cv2.matchTemplate(digit_roi, resized_template, cv2.TM_CCOEFF_NORMED)
            _, score, _, _ = cv2.minMaxLoc(result)

            if score > best_score:
                best_score = score
                best_match = digit

        # игнорируем цифру, если уверенность меньше 0.5
        if best_score < 0.2:
            continue

        # центр цифры (y + h/2)
        center_y = y + h // 2

        print(
            f"Найдена цифра: {best_match} | Позиция: ({x}, {y}) | Размер: {w}x{h} | Уверенность: {best_score:.2f} | Центр Y: {center_y}")
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, best_match, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        digits_info.append({
            'digit': best_match,
            'x': x,
            'y': y,
            'w': w,
            'h': h,
            'center_y': center_y,
            'confidence': best_score
        })

    cv2.imshow('Распознанные цифры', img)
    cv2.waitKey(0)  # Не ждем закрытия окна
    return digits_info


def find_tab_lines(image_path, white_threshold=230, min_line_margin=10):
    """
    Находит координаты шести струн табулатуры
    :param image_path: Путь к изображению
    :param white_threshold: Порог для белого (0-255, чем выше, тем чувствительнее)
    :param min_line_margin: Минимальный отступ линии от края изображения (в пикселях)
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("где пикча?")

    height, width = image.shape

    # Сканируем центральную часть изображения
    scan_margin = width // 4
    scan_area = image[:, scan_margin: width - scan_margin]

    # Находим первую линию сверху
    y1 = None
    for y in range(min_line_margin, height):  # Пропускаем верхний край
        row = scan_area[y, :]
        if np.mean(row) < white_threshold:  # Если строка не белая
            y1 = y
            break

    if y1 is None:
        raise ValueError("верхняя линия не найдена")

    # находим первую линию снизу
    y6 = None
    for y in range(height - 1 - min_line_margin, -1, -1):  # Пропускаем нижний край
        row = scan_area[y, :]
        if np.mean(row) < white_threshold:
            y6 = y
            break

    if y6 is None:
        raise ValueError("нижняя линия не найдена")

    # линии не должны быть очень близкими к краям изображения
    if y1 < min_line_margin or y6 > height - min_line_margin:
        raise ValueError("линии слишком близко к краям изображения, нужно переделать скриншот")

    # расстояние между струнами
    r = (y6 - y1) / 5
    y_coords = [round(y1 + i * r) for i in range(6)]

    return y_coords


def group_notes_by_x(digits_info, x_tolerance=15):
    """
    группировка в аккорды
    digits_info: Список информации о цифрах
    x_tolerance: Допустимое отклонение по X для группировки
    """
    if not digits_info:
        return []

    # Сортируем цифры по координате X
    sorted_digits = sorted(digits_info, key=lambda d: d['x'])

    groups = []
    current_group = [sorted_digits[0]]

    for digit in sorted_digits[1:]:
        # Проверяем, можно ли добавить цифру в текущую группу
        last_in_group = current_group[-1]
        if abs(digit['x'] - last_in_group['x']) <= x_tolerance:
            current_group.append(digit)
        else:
            groups.append(current_group)
            current_group = [digit]

    if current_group:
        groups.append(current_group)

    return groups


def assign_digits_to_strings(grouped_digits, string_y_coords, y_tolerance=10):
    """
    сопоставляет цифры со струнами и создает ноты/аккорды
    :param grouped_digits: Группы цифр
    :param string_y_coords: Координаты Y струн
    :param y_tolerance: Допустимое отклонение по Y для сопоставления
    :return: Список нот (одиночных или аккордов)
    """
    notes = []

    for group in grouped_digits:
        chord_notes = []

        for digit in group:
            center_y = digit['center_y']
            digit_value = digit['digit']

            # Находим ближайшую струну
            closest_string = None
            min_distance = float('inf')

            for i, string_y in enumerate(string_y_coords, 1):
                distance = abs(center_y - string_y)
                if distance < min_distance and distance <= y_tolerance:
                    min_distance = distance
                    closest_string = i

            if closest_string is not None:
                try:
                    fret = int(digit_value)
                    if (closest_string, fret) in guitar_to_piano:
                        chord_notes.append(guitar_to_piano[(closest_string, fret)])
                        print(f"Цифра {digit_value} на струне {closest_string} (лад {fret})")
                    else:
                        print(f"Ошибка: нота на струне {closest_string}, лад {fret} не найдена в словаре")
                except ValueError:
                    print(f"Ошибка: '{digit_value}' не является числом")

        if chord_notes:
            if len(chord_notes) == 1:
                notes.append(chord_notes[0])  # Одиночная нота
            else:
                notes.append(chord_notes)  # Аккорд

    return notes


def create_score(notes_list):
    """Создает партитуру из списка нот и аккордов"""
    score = stream.Score()
    part = stream.Part()
    bar = stream.Measure()
    bar.append(key.KeySignature(0))

    for notes in notes_list:
        if isinstance(notes, list):  # Аккорд
            ch = chord.Chord(notes)
            bar.append(ch)
        else:  # Одиночная нота
            n = note.Note(notes)
            bar.append(n)

    part.append(bar)
    score.append(part)
    return score


def main(image_path):
    # 1. шаблоны цифр
    templates = load_templates()

    # 2. цифры на изображении
    print("step 1: распознавание цифр...")
    digits_info = find_digits(image_path, templates)

    if not digits_info:
        print("цифры не найдены :((")
        return

    # 3. координаты струн
    print("\nstep 2: поиск струн...")
    try:
        string_y_coords = find_tab_lines(image_path)
        print("координаты струн (Y):", string_y_coords)
    except Exception as e:
        print(f"ошибка при поиске струн: {e}")
        return

    # 4. группировка цифр по X-координате для аккордов
    print("\nstep 3: группировка цифр...")
    grouped_digits = group_notes_by_x(digits_info)
    print(f"создано {len(grouped_digits)} групп (аккордов)")

    # 5. сопоставление цифры со струнами и создаем ноты/аккорды
    print("\nstep 4: сопоставление цифр и струн...")
    notes_list = assign_digits_to_strings(grouped_digits, string_y_coords)

    if not notes_list:
        print("струны не найдены")
        return

    # 6. музыкальная партитура
    print("\nstep 5: создание партитуры...")
    score = create_score(notes_list)

    # 7. итог
    output_path = 'output.mxl'
    score.write('musicxml', fp=output_path)
    print(f"\nпартитура сохранена в файл {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("путь к изображению табулатуры: ")
    main(image_path)
