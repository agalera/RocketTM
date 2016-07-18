import logging
from multiprocessing import Process
from rockettm import tasks
import traceback
import pika
import json
import sys
import os
from timekiller import call
import importlib


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
try:
    logging.basicConfig(**settings.logger)
except:
    pass

for mod in settings.imports:
    importlib.import_module(mod)


def worker(name, concurrency, durable=False, max_time=-1):
    def callback(ch, method, properties, body):
        # py3 support
        if isinstance(body, bytes):
            body = body.decode('utf-8')

        recv = json.loads(body)
        logging.info("execute %s" % recv['event'])
        try:
            print("recv", recv)
            for func, max_time2 in tasks.subs[recv['event']]:
                if max_time2 != -1:
                    apply_max_time = max_time2
                else:
                    apply_max_time = max_time
                call(func, apply_max_time, *recv['args'])
        except:
            logging.error(traceback.format_exc())
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    conn = pika.BlockingConnection(pika.ConnectionParameters(settings.ip))
    channel = conn.channel()
    logging.info("create queue: %s durable: %s" % (name, durable))
    channel.queue_declare(queue=name, durable=durable)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=name, no_ack=False)
    channel.start_consuming()


def main():
    for queue in settings.queues:
        for x in range(queue['concurrency']):
            p = Process(target=worker, kwargs=queue)
            logging.info("start process worker: %s queue: %s" % (worker,
                                                                 queue))
            p.start()

if __name__ == "__main__":
    main()
