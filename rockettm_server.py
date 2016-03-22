import logging
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
logging.basicConfig(**settings.logger)
map(__import__, settings.imports)


def worker(name, concurrency, durable=False):
    def callback(ch, method, properties, body):
        recv = json.loads(body)
        logging.info("execute %s" % recv['event'])
        try:
            for func in tasks.subs[recv['event']]:
                func(*recv['args'])
        except:
            logging.error(traceback.format_exc())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    conn = pika.BlockingConnection(pika.ConnectionParameters(settings.ip))
    channel = conn.channel()
    logging.info("create queue: %s durable: %s" % (name, durable))
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=name, no_ack=False)
    channel.start_consuming()

for queue in settings.queues:
    for x in xrange(queue['concurrency']):
        p = Process(target=worker, kwargs=queue)
        logging.info("start process worker: %s queue: %s" % (worker, queue))
        p.start()
