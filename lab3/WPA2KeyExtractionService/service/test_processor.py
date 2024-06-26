import subprocess
import json
import os
import time
import pika

DATABASE_URL = "sqlite:///./handshakes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_hashcat(hc22000_file, wordlist_file, output_file, db_session, handshake_id):
    hashcat_cmd = [
        'hashcat', '-m', '22000', '-a', '0',
        hc22000_file, wordlist_file,
        '--status', '--status-json', '--outfile', output_file,
        '--potfile-disable'
    ]

    process = subprocess.Popen(hashcat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='progress_queue')
    channel.queue_declare(queue='result_queue')

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip().startswith('{'):
            status = json.loads(output.strip())
            update_handshake_status(db_session, handshake_id, status)
            print_progress(status)

    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"Hashcat failed with error: {stderr_output.strip()}")

    process.stdout.close()
    process.stderr.close()

    read_output(output_file, channel)
    connection.close()

def print_progress(status):
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

    print(f"Progress: {progress[0]}/{progress[1]} ({(progress[0]/progress[1])*100:.2f}%)")
    print(f"Recovered Hashes: {recovered_hashes[0]}/{recovered_hashes[1]}")
    print(f"Elapsed Time: {elapsed_time_str}")
    print(f"Estimated Remaining Time: {remaining_time_str}")

    for device in devices:
        device_id = device.get("device_id")
        speed = device.get("speed")
        temp = device.get("temp")
        util = device.get("util")
        print(f"Device {device_id}: Speed={speed} H/s, Temp={temp}°C, Utilization={util}%")

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
    print("Progress sent:", progress_message)

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

def read_output(output_file, db_session, handshake_id):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            results = f.readlines()
            for result in results:
                print(result.strip())
                # Assuming password is found in the result
                update_handshake_password(db_session, handshake_id, result.strip())

def update_handshake_password(db_session, handshake_id, password):
    handshake = db_session.query(Handshake).filter(Handshake.id == handshake_id).first()
    if handshake:
        handshake.password = password
        handshake.processed = True
        db_session.commit()

if __name__ == "__main__":
    hc22000_file = '/mnt/u/NewPojects/Proga/Docker/Docker/lab3/WPA2KeyExtractionService/Tests/hc22000_files/clean-01.hc22000'
    wordlist_file = '/mnt/u/NewPojects/Proga/Docker/Docker/lab3/WPA2KeyExtractionService/dictionaries/rockyou.txt'
    output_file = 'hashcat_output.txt'

     # Initialize database session
    db_session = SessionLocal()

    # Replace with the actual handshake ID
    handshake_id = 1

    run_hashcat(hc22000_file, wordlist_file, output_file, db_session, handshake_id)
    read_output(output_file, db_session, handshake_id)

    db_session.close()
    
