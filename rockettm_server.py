import logging
from multiprocessing import Process, Manager
from rockettm import tasks
import traceback
import pika
import json
import sys
import os
from timekiller import call
import importlib
import requests
import time


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

try:
    callback_api = settings.callback_api
except:
    callback_api = None

for mod in settings.imports:
    importlib.import_module(mod)

tasks.ip = settings.ip


def call_api(json):
    if not callback_api:
        return
    try:
        requests.post(callback_api, json=json)
    except:
        pass


def safe_worker(func, return_dict, *args, **kwargs):
    try:
        return_dict['result'] = func(*args, **kwargs)
        return_dict['success'] = True
    except:
        return_dict['result'] = traceback.format_exc()
        return_dict['success'] = False

def worker(name, concurrency, durable=False, max_time=-1):
    def safe_call(func, *args, **kwargs):
        return_dict = Manager().dict()
        args = (func, return_dict) + args
        p = Process(target=safe_worker, args=args, kwargs=kwargs)
        p.start()
        p.join()
        return return_dict

    def callback(ch, method, properties, body):
        # py3 support
        ch.
        if isinstance(body, bytes):
            body = body.decode('utf-8')

        recv = json.loads(body)
        logging.info("execute %s" % recv['event'])
        try:
            if not recv['event'] in tasks.subs:
                call_api({'_id': recv['args'][0],
                          'result': 'task not defined',
                          'success': False})
                return False

            for func, max_time2 in tasks.subs[recv['event']]:
                logging.info("exec func: %s, timeout: %s" % (func, max_time2))
                if max_time2 != -1:
                    apply_max_time = max_time2
                else:
                    apply_max_time = max_time

                result = safe_call(call, func, apply_max_time,
                                   *recv['args'])
                result['_id'] = recv['args'][0]
                call_api(result)
                if not result['success']:
                    logging.error(result['result'])
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    while True:
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(settings.ip))
            channel = conn.channel()
            logging.info("create queue: %s durable: %s" % (name, durable))
            channel.queue_declare(queue=name, durable=durable)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(callback, queue=name, no_ack=True)
            channel.start_consuming()
        except (KeyboardInterrupt, SystemExit):
            print("server stop!")
            break
        except:
            logging.error("worker disconnect, try reconnect")
            time.sleep(5)


def main():
    for queue in settings.queues:
        for x in range(queue['concurrency']):
            p = Process(target=worker, kwargs=queue)
            logging.info("start process worker: %s queue: %s" % (worker,
                                                                 queue))
            p.start()

if __name__ == "__main__":
    main()
