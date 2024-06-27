import pika
import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./handshakes.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Handshake(Base):
    __tablename__ = "handshakes"
    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String, unique=True, index=True)
    bssid = Column(String)
    ssid = Column(String) 
    elapsed_time = Column(String)
    estimated_remaining_time = Column(String)
    progress = Column(Float, default=0.0)
    device_info = Column(String)
    password = Column(String)
    processed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

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
