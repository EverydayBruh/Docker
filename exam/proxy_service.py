from flask import Flask, request, jsonify
import requests
from queue import Queue
from threading import Thread

app = Flask(__name__)

# Конфигурация AI сервиса
AI_SERVICE_URL = 'http://ai.service.endpoint'  # URL сервиса партнёра
AI_TOKEN = 'your_company_token'  # Токен для доступа к сервису

# Очередь запросов
request_queue = Queue()

def process_queue():
    while True:
        endpoint, text, len, client_request = request_queue.get()
        try:
            response = requests.get(f"{AI_SERVICE_URL}/{len}/{text}", headers={"Authorization": f"Bearer {AI_TOKEN}"})
            client_request[0] = response.json()
        except Exception as e:
            client_request[0] = {"error": str(e)}
        finally:
            request_queue.task_done()


worker_thread = Thread(target=process_queue)
worker_thread.daemon = True
worker_thread.start()

@app.route('/<int:len>/<text>', methods=['GET'])
def generate_preview(len, text):
    if len(text.split()) < 2:
        return jsonify({"error": "Text must contain at least two words"}), 400

    client_request = [None]
    request_queue.put((AI_SERVICE_URL, text, len, client_request))
    request_queue.join()  

    return jsonify(client_request[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
