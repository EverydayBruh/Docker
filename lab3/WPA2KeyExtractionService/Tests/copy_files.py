import shutil
import os

source_file = "cap_files/handshake000.cap"
destination_folder = "cap_files"

if not os.path.exists(source_file):
    print(f"Файл {source_file} не существует.")
else:
    # Создание 100 копий файла
    for i in range(1, 30):
        destination_file = os.path.join(destination_folder, f"handshake{i:03}.cap")
        shutil.copy(source_file, destination_file)
        print(f"Создан файл: {destination_file}")

print("Копирование завершено.")
