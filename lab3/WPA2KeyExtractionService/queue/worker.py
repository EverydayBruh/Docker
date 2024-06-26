import pika
import json
import os
from service.processor import process_handshake

def callback(ch, method, properties, body):
    data = json.loads(body)
    filepath = data['filepath']
    process_handshake(filepath)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='handshake_queue')
channel.basic_consume(queue='handshake_queue', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
