import logging
from multiprocessing import Process, Manager, Event
from rockettm import tasks
import traceback
from kombu import Connection, Exchange, Queue
import sys
import os
from timekiller import call
import importlib
import time
from basicevents import run, send, subscribe
import signal


if len(sys.argv) >= 2:
    i, f = os.path.split(sys.argv[-1])
    sys.path.append(i)
    settings = __import__(os.path.splitext(f)[0])
else:
    sys.path.append(os.getcwd())
    try:
        import settings
    except:
        exit("settings.py not found")

logging.basicConfig(**settings.logger)


for mod in settings.imports:
    importlib.import_module(mod)


tasks.ip = settings.RABBITMQ_IP

if not hasattr(settings, 'ROCKETTM_CALLBACK'):
    settings.ROCKETTM_CALLBACK = True

event_kill = Event()
finish_tasks = Event()


def handler_stop_signals(signum, frame):
    logging.warning("server recieve sigterm")
    if event_kill.is_set():
        logging.warning("server forcing stop")
        exit(1)
    event_kill.set()


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


@subscribe('results')
def call_results(json, room='results'):
    tasks.send_task('results', room, json)


class Worker(Process):
    def __init__(self, event_kill, name, concurrency, ip, durable=False,
                 max_time=-1):
        self.queue_name = name
        self.concurrency = concurrency
        self.ip = ip
        self.durable = durable
        self.max_time = max_time
        self.event_kill = event_kill
        super(Worker, self).__init__()

    def safe_worker(self, func, return_dict, apply_max_time, body):
        try:
            return_dict['result'] = call(func, apply_max_time,
                                         *body['args'], **body['kwargs'])
            return_dict['success'] = True
        except:
            return_dict['result'] = traceback.format_exc()
            return_dict['success'] = False
            logging.error(return_dict['result'])

    def safe_call(self, func, apply_max_time, body):
        return_dict = Manager().dict()
        p = Process(target=self.safe_worker, args=(func, return_dict,
                                                   apply_max_time, body))
        p.start()
        p.join()
        return return_dict

    def callback(self, body, message):
        message.ack()
        logging.info("execute %s" % body['event'])
        _id = body['args'][0]
        if settings.ROCKETTM_CALLBACK:
            send('results', {'_id': _id, 'status': 'processing'})
        if not body['event'] in tasks.subs:
            if settings.ROCKETTM_CALLBACK:
                send('results', {'_id': _id,
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
                apply_max_time = self.max_time
            result.append(dict(self.safe_call(func, apply_max_time, body)))

        success = not any(r['success'] is False for r in result)
        send('results', {'_id': _id, 'status': 'finished',
                         'success': success, 'result': result})
        return True

    def run(self):
        while not self.event_kill.is_set():
            try:
                with Connection('amqp://guest:guest@%s//' % self.ip) as conn:
                    conn.ensure_connection()
                    exchange = Exchange(self.queue_name, 'direct',
                                        durable=self.durable)
                    queue = Queue(name=self.queue_name,
                                  exchange=exchange,
                                  durable=self.durable,
                                  routing_key=self.queue_name)
                    queue(conn).declare()
                    logging.info("create queue: %s durable: %s" %
                                 (self.queue_name, self.durable))
                    channel = conn.channel()
                    channel.basic_qos(prefetch_size=0, prefetch_count=1,
                                      a_global=False)
                    with conn.Consumer(queue, callbacks=[self.callback],
                                       channel=channel) as consumer:
                        while not self.event_kill.is_set():
                            # logging.info(consumer)
                            try:
                                conn.drain_events(timeout=5)
                            except:
                                pass

            except (KeyboardInterrupt, SystemExit):
                logging.warning("server stop!")
                break

            except:
                logging.error(traceback.format_exc())
                logging.error("connection loss, try reconnect")
                time.sleep(5)


def main():
    # start basicevents
    run(finish_tasks.is_set)
    list_process = []
    for queue in settings.queues:
        for x in range(queue['concurrency']):
            p = Worker(event_kill, ip=settings.RABBITMQ_IP, **queue)
            logging.info("start process worker: %s queue: %s" % (p,
                                                                 queue))
            list_process.append(p)
            p.start()

    try:
        for p in list_process:
            p.join()
    except:
        logging.warning("force stop")
    finish_tasks.set()


if __name__ == "__main__":
    main()
