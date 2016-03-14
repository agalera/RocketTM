from multiprocessing import Process
from rockettm import tasks
import traceback
import pika
import json
import sys
import os
if len(sys.argv) == 2:
    i, f = os.path.split(sys.argv[1])
    sys.path.append(i)
    settings = __import__(os.path.splitext(f)[0])
else:
    sys.path.append(os.getcwd())
    try:
        import settings
    except:
        exit("settings.py not found")
map(__import__, settings.imports)


def worker(queue_name):
    def callback(ch, method, properties, body):
        recv = json.loads(body)
        try:
            for func in tasks.subs[recv['event']]:
                func(*recv['args'])
        except:
            print(traceback.format_exc())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    conn = pika.BlockingConnection(pika.ConnectionParameters(settings.ip))
    channel = conn.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=queue_name, no_ack=False)
    channel.start_consuming()

for queue in settings.queues:
    for x in xrange(queue['concurrency']):
        p = Process(target=worker, args=(queue['name'], ))
        p.start()
