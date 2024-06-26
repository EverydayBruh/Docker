import subprocess
import time
import json
import os

def run_hashcat(hc22000_file, wordlist_file, output_file):
    hashcat_cmd = [
        'hashcat', '-m', '22000', '-a', '0',
        hc22000_file, wordlist_file,
        '--status', '--status-json', '--outfile', output_file,
        '--potfile-disable'
    ]

    process = subprocess.Popen(hashcat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output.strip().startswith('{'):
            status = json.loads(output.strip())
            print_progress(status)

    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"Hashcat failed with error: {stderr_output.strip()}")

    process.stdout.close()
    process.stderr.close()

def print_progress(status):
    progress = status.get("progress", [0, 0])
    recovered_hashes = status.get("recovered_hashes", [0, 1])
    devices = status.get("devices", [])

    print(f"Progress: {progress[0]}/{progress[1]} ({(progress[0]/progress[1])*100:.2f}%)")
    print(f"Recovered Hashes: {recovered_hashes[0]}/{recovered_hashes[1]}")
    
    for device in devices:
        device_id = device.get("device_id")
        speed = device.get("speed")
        temp = device.get("temp")
        util = device.get("util")
        print(f"Device {device_id}: Speed={speed} H/s, Temp={temp}°C, Utilization={util}%")

def read_output(output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            results = f.readlines()
            for result in results:
                print(result.strip())