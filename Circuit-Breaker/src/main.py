from flask import Flask, jsonify
from circuit_breaker import CircuitBreaker
import requests
import time

app = Flask(__name__)
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10)

@app.route('/call_external_service')
def call_external_service():
    try:
        response = breaker.call(requests.get, 'http://external_service:8080')
        return jsonify({"status": "success", "data": response.text}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
