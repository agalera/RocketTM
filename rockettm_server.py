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
from basicevents import run, send, subscribe


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


@subscribe('api')
def call_api(json):
    if callback_api:
        try:
            return requests.post(callback_api, json=json, timeout=10)
        except:
            logging.error(traceback.format_exc())


def safe_worker(func, return_dict, apply_max_time, body):
    try:
        return_dict['result'] = call(func, apply_max_time,
                                     *body['args'], **body['kwargs'])
        return_dict['success'] = True
    except:
        return_dict['result'] = traceback.format_exc()
        return_dict['success'] = False
        logging.error(return_dict['result'])


def worker(name, concurrency, durable=False, max_time=-1):
    def safe_call(func, apply_max_time, body):
        return_dict = Manager().dict()
        p = Process(target=safe_worker, args=(func, return_dict,
                                              apply_max_time, body))
        p.start()
        p.join()
        return return_dict

    def callback(body, message):
        message.ack()
        logging.info("execute %s" % body['event'])
        _id = body['args'][0]
        send('api', {'_id': _id, 'status': 'processing'})
        if not body['event'] in tasks.subs:
            send('api', {'_id': _id,
                         'result': 'task not defined',
                         'status': 'finished',
                         'success': False})
            return False

        result = []
        for func, max_time2 in tasks.subs[body['event']]:
            logging.info("exec func: %s, timeout: %s" % (func, max_time2))
            if max_time2 != -1:
                apply_max_time = max_time2
            else:
                apply_max_time = max_time
            result.append(dict(safe_call(func, apply_max_time,
                                         body)))

        success = not any(r['success'] is False for r in result)
        send('api', {'_id': _id, 'status': 'finished',
                     'success': success, 'result': result})
        return True

    while True:
        try:
            with Connection('amqp://guest:guest@%s//' % settings.ip) as conn:
                conn.ensure_connection()
                exchange = Exchange(name, 'direct', durable=durable)
                queue = Queue(name=name,
                              exchange=exchange,
                              durable=durable, routing_key=name)
                queue(conn).declare()
                logging.info("create queue: %s durable: %s" % (name, durable))
                channel = conn.channel()
                channel.basic_qos(prefetch_size=0, prefetch_count=1,
                                  a_global=False)
                with conn.Consumer(queue, callbacks=[callback],
                                   channel=channel) as consumer:
                    while True:
                        logging.info(consumer)
                        conn.drain_events()

        except (KeyboardInterrupt, SystemExit):
            logging.warning("server stop!")
            break

        except:
            logging.error(traceback.format_exc())
            logging.error("connection loss, try reconnect")
            time.sleep(5)


def main():
    # start basicevents
    run()
    list_process = []
    for queue in settings.queues:
        for x in range(queue['concurrency']):
            p = Process(target=worker, kwargs=queue)
            logging.info("start process worker: %s queue: %s" % (worker,
                                                                 queue))
            list_process.append(p)
            p.start()

    try:
        for p in list_process:
            p.join()
    except:
        logging.info("stop")
    finally:
        send("STOP")


if __name__ == "__main__":
    main()
