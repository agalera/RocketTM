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
    producer = False

    # deprecated
    @staticmethod
    def connect(ip=None):
        if ip:
            tasks.ip = ip
        logging.warning('reconnect amqp')
        tasks.conn = Connection('amqp://guest:guest@%s//' % tasks.ip)
        tasks.producer = tasks.conn.Producer(serializer='json')

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
        exchange = Exchange(queue_name, 'direct', durable=True)
        queue = Queue(queue_name, exchange=exchange, routing_key=queue_name,
                      durable=True)

        send_ok = False
        for retry in range(10):
            if not tasks.conn or not tasks.conn.connected:
                tasks.connect()
            try:
                tasks.producer.publish({'event': event, 'args': args,
                                        'kwargs': kwargs},
                                       exchange=exchange,
                                       routing_key=queue_name,
                                       declare=[queue])
                send_ok = True
                break
            except:
                logging.error(traceback.format_exc())
                time.sleep(retry * 1.34)
        if send_ok:
            logging.warning("send its ok!")
            return _id
        else:
            logging.error("send Failed")
            return False


# avoids having to import tasks
connect = tasks.connect
send_task = tasks.send_task
add_task = tasks.add_task
task = tasks.task
