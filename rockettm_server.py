import logging
from multiprocessing import Process, Manager
from rockettm import tasks
import traceback
from kombu import Connection, Exchange, Queue
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

logging.basicConfig(**settings.logger)


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

    def callback(body, message):
        # py3 support

        logging.info("execute %s" % body['event'])
        if not body['event'] in tasks.subs:
            call_api({'_id': body['args'][0],
                      'result': 'task not defined',
                      'success': False})
            return False

        for func, max_time2 in tasks.subs[body['event']]:
            logging.info("exec func: %s, timeout: %s" % (func, max_time2))
            if max_time2 != -1:
                apply_max_time = max_time2
            else:
                apply_max_time = max_time

            result = safe_call(call, func, apply_max_time,
                               *body['args'])
            result['_id'] = body['args'][0]
            call_api(result)
            if not result['success']:
                logging.error(result['result'])

        message.ack()

    while True:
        try:
            with Connection('amqp://guest:guest@%s//' % settings.ip) as conn:
                exchange = Exchange(name, 'direct', durable=durable)
                queue = Queue(name=name,
                              exchange=exchange,
                              durable=durable, routing_key=name)
                queue(conn).declare()
                logging.info("create queue: %s durable: %s" % (name, durable))
                with conn.Consumer(queue, callbacks=[callback]) as consumer:
                    logging.info(consumer)
                    while True:
                        conn.drain_events()

        except (KeyboardInterrupt, SystemExit):
            logging.warning("server stop!")
            break

        except:
            import traceback
            logging.error(traceback.format_exc())
            logging.error("connection loss, try reconnect")
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
