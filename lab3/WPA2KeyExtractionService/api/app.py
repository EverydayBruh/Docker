import os
import uuid
import json
from flask import Flask, request, jsonify
import pika
from werkzeug.utils import secure_filename
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import logging_loki
import time
import traceback


handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"service": "API"},
    version="1",
)

logger = logging.getLogger("API")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_exception(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", 
                 extra={
                     "exc_info": (exc_type, exc_value, traceback.format_tb(exc_traceback))
                 })

import sys
sys.excepthook = log_exception

REQUEST_COUNT = Counter(
    'request_count', 'App Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency',
    ['method', 'endpoint']
)


app = Flask(__name__)

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'hc22000', 'cap'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_rabbitmq_request(request_data, method):
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='api_request_queue')

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    correlation_id = str(uuid.uuid4())

    channel.basic_publish(
        exchange='',
        routing_key='api_request_queue',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=correlation_id,
            headers={'method': method}  # Добавляем метод HTTP-запроса в заголовки
        ),
        body=json.dumps(request_data)
    )

    for method_frame, properties, body in channel.consume(callback_queue):
        if properties.correlation_id == correlation_id:
            channel.basic_ack(method_frame.delivery_tag)
            connection.close()
            return json.loads(body)
        
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):   
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(request_latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    logger.info(f"Request processed", extra={
        "path": request.path,
        "method": request.method,
        "status_code": response.status_code,
        "request_time": request_latency
    })
    return response

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        request_data = {
            'filepath': filepath,
            'bssid': request.form.get('bssid'),
            'ssid': request.form.get('ssid')
        }
        
        response = send_rabbitmq_request(request_data, 'POST')
        
        return jsonify(response), 200
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/status/<path:filename>', methods=['GET'])
def get_status(filename):
    request_data = {
        'filepath': os.path.join(app.config['UPLOAD_FOLDER'], filename)
    }
    
    response = send_rabbitmq_request(request_data, 'GET')
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)