

#credentials = pika.PlainCredentials('guest', 'guest')
import json
from django.conf import settings
import pika
import http.client

    
def publish_email(data):
    
    try:
        # conn = http.client.HTTPSConnection('')
        # conn.request("GET", '/')
        # response = conn.getresponse()
        # parameters = pika.URLParameters(settings.RABBIT_URL)
        # connection = pika.BlockingConnection(parameters)
        # channel = connection.channel()
        # channel.queue_declare(queue='email.send')
        # channel.basic_publish(exchange='', routing_key='email.send', body=json.dumps(data))
        
        return True
    except Exception as e:
        print(e)
        return False
    