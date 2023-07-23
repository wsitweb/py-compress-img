from tkinter import Tk, Label, Button, StringVar, Entry, filedialog
from tkinter import ttk
from PIL import Image, ExifTags
import os
from tqdm import tqdm

def compress_and_rotate_images():
    # Получаем значения из полей ввода
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    desired_width = int(desired_width_var.get())

    # Проверка, что путь к папке с изображениями не пустой
    if not input_folder:
        result_label.config(text="Ошибка: Укажите папку с изображениями.")
        return

    # Объединяем пути для ввода и вывода
    input_path = os.path.normpath(input_folder)
    output_path = os.path.normpath(output_folder)

    # Проверяем существование папки с изображениями
    if not os.path.exists(input_path) or not os.path.isdir(input_path):
        result_label.config(text="Ошибка: Папка с изображениями не существует.")
        return

    # Проверяем существование папки вывода, если ее нет - создаем
    if output_folder and not os.path.exists(output_path):
        os.makedirs(output_path)

    # Обход всех файлов в папке с изображениями
    try:
        for filename in tqdm(os.listdir(input_path), desc="Сжатие и поворот"):
            # Открываем изображение
            img = Image.open(os.path.join(input_path, filename))

            # Поворачиваем изображение на основе информации о его ориентации в EXIF
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif is not None:
                    exif = dict(exif.items())
                    orientation = exif.get(orientation, None)
                    if orientation is not None:
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)

            # Вычисляем пропорциональную высоту на основе заданной ширины
            width_percent = (desired_width / float(img.size[0]))
            new_height = int((float(img.size[1]) * float(width_percent)))

            # Сжимаем изображение по ширине с использованием LANCZOS-фильтра
            resized_img = img.resize((desired_width, new_height), Image.LANCZOS)

            # Сохраняем сжатое и повернутое изображение в папку назначения
            output_file_path = os.path.join(output_path, filename)
            resized_img.save(output_file_path)

        result_label.config(text="Сжатие и поворот завершены!")
    except OSError as e:
        result_label.config(text=f"Ошибка: {e}")

# Создание окна приложения
root = Tk()

# Задание увеличенной ширины и высоты окна (в пикселях)
default_window_width = 300
default_window_height = 250
root.geometry(f"{default_window_width}x{default_window_height}")

root.title("Сжатие изображений")

# Поля ввода для папок и ширины изображений
input_folder_var = StringVar()
output_folder_var = StringVar()
desired_width_var = StringVar()

input_folder_label = Label(root, text="Папка с изображениями:")
input_folder_label.pack()
input_folder_entry = Entry(root, textvariable=input_folder_var, insertbackground="black")
input_folder_entry.pack()

output_folder_label = Label(root, text="Папка для сохранения:")
output_folder_label.pack()
output_folder_entry = Entry(root, textvariable=output_folder_var, insertbackground="black")
output_folder_entry.pack()

desired_width_label = Label(root, text="Желаемая ширина (в пикселях):")
desired_width_label.pack()

# Список с вариантами ширины сжатия, начиная с 4K и заканчивая 1280 (не включительно)
compression_widths = [7680, 3840, 2560, 1920, 1600, 1366, 1280, 854, 640, 426, 180, 152, 120, 76, 60, 48, 32, 16]

# Установка значения по умолчанию (4K)
desired_width_var.set(1920)

# Создание выпадающего списка для выбора желаемой ширины
desired_width_combobox = ttk.Combobox(root, textvariable=desired_width_var, values=compression_widths)
desired_width_combobox.pack()

# Кнопка для запуска процесса сжатия и поворота
compress_button = Button(root, text="Сжать", command=compress_and_rotate_images)
compress_button.pack()

# Метка для вывода результата
result_label = Label(root, text="")
result_label.pack()

# Запуск основного цикла обработки событий
root.mainloop()