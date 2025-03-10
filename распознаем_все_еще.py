import cv2
import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Xiaomi\OneDrive\инфа\Tesseract-OCR\tesseract.exe' #путь к Tesseract OCR на данном ноуте

def look_img(image_path):
    # загрузить изображение
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # применение порогового значения для получения бинарного изображения
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # распознание tesseract
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(binary, output_type=Output.DICT, config=custom_config)

    # обработка распознанных данных
    total_boxes = len(details['text'])
    for sequence_number in range(total_boxes):
        if int(details['conf'][sequence_number]) > 30:  # уровень уверенности
            (x, y, w, h) = (details['left'][sequence_number],
                            details['top'][sequence_number],
                            details['width'][sequence_number],
                            details['height'][sequence_number])
            text = details['text'][sequence_number]
            print(f"цифра: {text}, координаты: ({x}, {y}), размер: ({w}, {h})")

            # зеленый прямоугольник
            image = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # вывести видение
    cv2.imshow('окно визуального вывода', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# пора тестить
look_img('t2.png')