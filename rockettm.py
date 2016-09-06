from kombu import Connection, Exchange, Queue
import logging
import uuid
import traceback
import time


class tasks(object):
    subs = {}
    queues = []
    ip = "localhost"
    conn = False
    channel = False

    # deprecated
    @staticmethod
    def connect(ip=None):
        if ip:
            tasks.ip = ip

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
    def send_task(queue_name, event, *args):
        _id = str(uuid.uuid4())
        args = list((_id,) + args)
        logging.info("send task to queue %s, event %s" % (queue_name, event))
        exchange = Exchange(queue_name, 'direct', durable=True)
        queue = Queue(queue_name, exchange=exchange, routing_key=queue_name)
        with Connection('amqp://guest:guest@%s//' % tasks.ip) as conn:
            # produce
            producer = conn.Producer(serializer='json')
            for retry in range(10):
                try:
                    producer.publish({'event': event, 'args': args},
                                     exchange=exchange,
                                     routing_key=queue_name,
                                     declare=[queue])
                    break
                except:
                    logging.error(traceback.format_exc())
                    time.sleep(retry * 1.34)
        logging.warning("send its ok!")
        return _id


# avoids having to import tasks
connect = tasks.connect
send_task = tasks.send_task
add_task = tasks.add_task
task = tasks.task
