import json

# Параметры
base_path = "U:\\NewPojects\\Proga\\Docker\\Docker\\lab3\\WPA2KeyExtractionService\\Tests\\cap_files\\handshake"
bssid_prefix = "bssid"
ssid_prefix = "ssid"
num_files = 100

# Создание списка объектов
data = []
for i in range(1, num_files + 1):
    file_number = f"{i:03}"
    file_path = f"{base_path}{file_number}.cap"
    bssid = f"{bssid_prefix}{i}"
    ssid = f"{ssid_prefix}{i}"
    data.append({
        "filePath": file_path,
        "bssid": bssid,
        "ssid": ssid
    })

# Запись в JSON файл
output_file = "cap_files_data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"JSON файл создан: {output_file}")
