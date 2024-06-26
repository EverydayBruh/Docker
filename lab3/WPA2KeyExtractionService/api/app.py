from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pika
import json
import os

app = Flask(__name__)
api = Api(app)

UPLOAD_FOLDER = '/app/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class Upload(Resource):
    def post(self):
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='handshake_queue')
            channel.basic_publish(exchange='',
                                  routing_key='handshake_queue',
                                  body=json.dumps({'filepath': filepath}))
            connection.close()
            return {'message': 'File uploaded successfully'}, 201
        return {'message': 'No file uploaded'}, 400

api.add_resource(Upload, '/upload')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
