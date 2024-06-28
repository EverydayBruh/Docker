import subprocess
import json
import time
import pika
import os

# Константы путей к словарям
WORDLIST_PATHS = {
    1: '/mnt/u/NewPojects/Proga/Docker/Docker/lab3/WPA2KeyExtractionService/dictionaries/rockyou.txt',
    2: '/mnt/u/NewPojects/Proga/Docker/Docker/lab3/WPA2KeyExtractionService/dictionaries/rockyou.txt',
    3: '/mnt/u/NewPojects/Proga/Docker/Docker/lab3/WPA2KeyExtractionService/dictionaries/rockyou.txt',
    4: '/mnt/u/NewPojects/Proga/Docker/Docker/lab3/WPA2KeyExtractionService/dictionaries/rockyou.txt'
}


def run_hashcat(hc22000_file, wordlist_file, output_file, channel):
    hashcat_cmd = [
        'hashcat' , '-m', '22000', '-a', '0',
        hc22000_file, wordlist_file,
        '--status', '--status-json', '--outfile', output_file
    ]

    process = subprocess.Popen(hashcat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip().startswith('{'):
            status = json.loads(output.strip())
            send_progress(channel, status)
        print(output.strip())  # Вывод в консоль для дебаггинга

    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"Hashcat failed with error: {stderr_output.strip()}")

    process.stdout.close()
    process.stderr.close()

    # Отправка результата после завершения работы Hashcat
    read_output(output_file, channel)

def send_progress(channel, status):
    progress = status.get("progress", [0, 0])
    recovered_hashes = status.get("recovered_hashes", [0, 1])
    devices = status.get("devices", [])
    time_start = status.get("time_start")
    estimated_stop = status.get("estimated_stop")

    current_time = time.time()
    elapsed_time = current_time - time_start
    remaining_time = estimated_stop - current_time

    elapsed_time_str = format_time(elapsed_time)
    remaining_time_str = format_time(remaining_time)

    progress_message = {
        'progress': f"{progress[0]}/{progress[1]} ({(progress[0]/progress[1])*100:.2f}%)",
        'recovered_hashes': f"{recovered_hashes[0]}/{recovered_hashes[1]}",
        'elapsed_time': elapsed_time_str,
        'remaining_time': remaining_time_str,
        'devices': [
            {
                'device_id': device.get("device_id"),
                'speed': device.get("speed"),
                'temp': device.get("temp"),
                'util': device.get("util")
            } for device in devices
        ]
    }

    channel.basic_publish(exchange='', routing_key='progress_queue', body=json.dumps(progress_message))
    print("Progress sent:", progress_message)  # Вывод в консоль для дебаггинга

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

def read_output(output_file, channel):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            results = f.readlines()
            for result in results:
                result_message = {'result': result.strip()}
                channel.basic_publish(exchange='', routing_key='result_queue', body=json.dumps(result_message))
                print("Result sent:", result_message)  # Вывод в консоль для дебаггинга

def on_request(ch, method, properties, body):
    request = json.loads(body)
    hc22000_file = request.get('hc22000_file')
    wordlist_size = request.get('wordlist_size')
    output_file = 'hashcat_output.txt'

    wordlist_file = WORDLIST_PATHS.get(wordlist_size)
    if not wordlist_file:
        print(f"Invalid wordlist size: {wordlist_size}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f"Received request: {request}")  # Вывод в консоль для дебаггинга
    run_hashcat(hc22000_file, wordlist_file, output_file, ch)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_service():
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

    # Connection setup
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='request_queue')
    channel.queue_declare(queue='progress_queue')
    channel.queue_declare(queue='result_queue')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='request_queue', on_message_callback=on_request)

    print("Waiting for requests...")  # Вывод в консоль для дебаггинга
    channel.start_consuming()

start_service()
