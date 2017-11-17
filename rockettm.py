from redisqueue import RedisQueue
from redis import Redis
import logging
import uuid
import traceback
import time


class tasks(object):
    subs = {}
    ip = "localhost"
    conn = False
    producer = False
    serializer = "json"

    # deprecated
    @staticmethod
    def connect(ip='localhost'):
        if ip != 'localhost':
            tasks.ip = ip
        tasks.conn = RedisQueue(Redis(host=tasks.ip),
                                serializer=tasks.serializer)
        logging.warning('connected redis')

    @staticmethod
    def add_task(event, func, max_time=-1):
        logging.info("add task %s" % event)
        if event not in tasks.subs:
            tasks.subs[event] = []
        tasks.subs[event].append((func, max_time))

    @staticmethod
    def task(event, max_time=-1):
        def wrap_function(func):
            tasks.add_task(event, func, max_time)
            return func
        return wrap_function

    @staticmethod
    def send_task(queue_name, event, *args, **kwargs):
        if 'rocket_id' in kwargs:
            _id = kwargs.pop('rocket_id')
        else:
            _id = str(uuid.uuid4())

        args = list((_id,) + args)
        logging.info("send task to queue %s, event %s" % (queue_name, event))

        if not tasks.conn:
            tasks.connect()

        send_ok = False
        for retry in range(10):
            try:
                tasks.conn.put({'event': event,
                                'args': args,
                                'kwargs': kwargs},
                               queue_name)
                send_ok = True
                break
            except:
                logging.error(traceback.format_exc())
                time.sleep(retry * 1.34)
                tasks.connect()
                print(traceback.format_exc())
        if send_ok:
            logging.info("send ok!")
            return _id
        else:
            logging.error("send Failed")
            return False


# avoids having to import tasks
connect = tasks.connect
send_task = tasks.send_task
add_task = tasks.add_task
task = tasks.task
