import logging
from multiprocessing import Process, Manager
from rockettm import tasks
import traceback
import sys
import os
from timekiller import call
import importlib
import requests
import time
from basicevents import run, send, subscribe
import stomp
import json


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

tasks.ip, tasks.port = settings.ip, settings.port


@subscribe('api')
def call_api(json):
    if callback_api:
        try:
            requests.post(callback_api, json=json)
        except:
            pass


def safe_worker(func, return_dict, apply_max_time, body):
    try:
        return_dict['result'] = call(func, apply_max_time,
                                     *body['args'], **body['kwargs'])
        return_dict['success'] = True
    except:
        return_dict['result'] = traceback.format_exc()
        return_dict['success'] = False
        logging.error(return_dict['result'])


class WorkerListener(stomp.ConnectionListener):
    def __init__(self, conn, max_time=-1):
        self.max_time = max_time
        self.conn = conn

    def on_message(self, headers, message):
        message = json.loads(message)
        logging.info("execute %s" % message['event'])
        _id = message['args'][0]
        send('api', {'_id': _id, 'status': 'processing'})
        if not message['event'] in tasks.subs:
            send('api', {'_id': _id,
                         'result': 'task not defined',
                         'status': 'finished',
                         'success': False})
            return

        result = []
        for func, max_time2 in tasks.subs[message['event']]:
            logging.info("exec func: %s, timeout: %s" % (func, max_time2))
            if max_time2 != -1:
                apply_max_time = max_time2
            else:
                apply_max_time = self.max_time
            result.append(dict(self.safe_call(func, apply_max_time,
                                              message)))

        success = not any(r['success'] is False for r in result)
        send('api', {'_id': _id, 'status': 'finished',
                     'success': success, 'result': result})
        self.conn.ack(id=headers['message-id'],
                      subscription=headers['subscription'])

    def safe_call(self, func, apply_max_time, body):
        return_dict = Manager().dict()
        p = Process(target=safe_worker, args=(func, return_dict,
                                              apply_max_time, body))
        p.start()
        p.join()
        return return_dict


def worker(name, concurrency, durable=False, max_time=-1):
    while True:
        try:
            conn = stomp.Connection([(tasks.ip, tasks.port)],
                                    keepalive=True)
            conn.set_listener('', WorkerListener(conn, max_time))
            conn.start()
            conn.connect(settings.user, settings.password, wait=True)
            conn.subscribe(destination="/queue/%s" % name,
                           id=1, ack='client-individual',
                           headers={'prefetch-count': 1})
            while conn.is_connected():
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            conn.disconnect()
            logging.warning("server stop!")
            break


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

    for p in list_process:
        p.join()


if __name__ == "__main__":
    main()
