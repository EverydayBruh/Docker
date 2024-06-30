import asyncio
import aiohttp
import os
import time
import json

UPLOAD_URL = 'http://localhost:5000/upload'
STATUS_URL = 'http://localhost:5000/status/'
FILES_DIR = './cap_files'
PROCESS_TIMEOUT = 600  # максимальное время ожидания завершения обработки
RESULTS_FILE = 'results.json'

async def upload_file(session, file_path):
    filename = os.path.basename(file_path)
    data = aiohttp.FormData()
    data.add_field('file', open(file_path, 'rb'), filename=filename, content_type='application/octet-stream')
    data.add_field('bssid', '00:00:00:00:00:00')
    data.add_field('ssid', 'test_ssid')
    async with session.post(UPLOAD_URL, data=data) as response:
        response_json = await response.json()
        return response_json, time.time()

async def get_status(session, filename):
    async with session.get(f"{STATUS_URL}{filename}") as response:
        response_json = await response.json()
        return response_json, time.time()

async def process_file(file_path):
    async with aiohttp.ClientSession() as session:
        upload_response, upload_time = await upload_file(session, file_path)
        
        filename = os.path.basename(file_path)
        status = 'in_process'
        status_times = []
        while status != 'processed' and (time.time() - upload_time) < PROCESS_TIMEOUT:
            status_response, status_time = await get_status(session, filename)
            status = status_response.get('status', 'error')
            status_times.append(status_time)
            await asyncio.sleep(1)  # пауза между запросами статуса

        return {
            'filename': filename,
            'upload_time': upload_time,
            'status_times': status_times,
            'final_status': status
        }

async def main():
    files = [os.path.join(FILES_DIR, f) for f in os.listdir(FILES_DIR) if f.endswith('.cap')]
    tasks = [process_file(file) for file in files]
    results = await asyncio.gather(*tasks)

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == '__main__':
    asyncio.run(main())
