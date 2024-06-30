import json
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

RESULTS_FILE = 'results.json'
PLOT_FILE = 'requests_per_second.png'

def load_results():
    with open(RESULTS_FILE, 'r') as f:
        results = json.load(f)
    return results

def count_requests_per_second(results):
    upload_counts = defaultdict(int)
    status_counts = defaultdict(int)

    min_time = float('inf')

    for result in results:
        upload_time = int(result['upload_time'])
        upload_counts[upload_time] += 1
        min_time = min(min_time, upload_time)

        for status_time in result['status_times']:
            status_time = int(status_time)
            status_counts[status_time] += 1
            min_time = min(min_time, status_time)

    return upload_counts, status_counts, min_time

def smooth(y, window_size):
    half_window = window_size // 2
    y_padded = np.pad(y, (half_window, half_window), mode='edge')
    y_smooth = np.convolve(y_padded, np.ones(window_size) / window_size, mode='valid')
    return y_smooth

def plot_requests_per_second(upload_counts, status_counts, min_time):
    all_times = sorted(set(upload_counts.keys()).union(status_counts.keys()))
    
    adjusted_times = [time - min_time for time in all_times]
    upload_requests = [upload_counts[time] for time in all_times]
    status_requests = [status_counts[time] for time in all_times]

    window_size = 5
    upload_requests_smooth = smooth(upload_requests, window_size)
    status_requests_smooth = smooth(status_requests, window_size)

    plt.figure(figsize=(10, 6))
    plt.plot(adjusted_times, upload_requests_smooth, label='Upload Requests', color='blue', alpha=0.7)
    plt.plot(adjusted_times, status_requests_smooth, label='Status Requests', color='red', alpha=0.7)
    plt.bar(adjusted_times, upload_requests, color='blue', alpha=0.3, width=0.8)
    plt.bar(adjusted_times, status_requests, color='red', alpha=0.3, width=0.8)
    plt.xlabel('Time (s)')
    plt.ylabel('Number of Requests')
    plt.title('Requests Per Second')
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close()

if __name__ == '__main__':
    results = load_results()
    upload_counts, status_counts, min_time = count_requests_per_second(results)
    plot_requests_per_second(upload_counts, status_counts, min_time)
