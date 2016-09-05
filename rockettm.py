from pika import BlockingConnection, ConnectionParameters
import json
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

    @staticmethod
    def connect(ip=None):
        try:
            logging.info("rabbitmq connect %s" % tasks.ip)
            if ip:
                tasks.ip = ip
            tasks.conn = BlockingConnection(ConnectionParameters(tasks.ip))
            tasks.channel = tasks.conn.channel()
        except:
            pass

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
    def send_task(queue, event, *args):
        _id = str(uuid.uuid4())
        args = list((_id,) + args)
        logging.info("send task to queue %s, event %s" % (queue, event))
        retries = 0
        success = False
        for retries in range(10):
            try:
                if (not tasks.channel or not tasks.conn or
                        tasks.channel.is_closed or tasks.conn.is_closed):
                    logging.error("connection is closed, try reconnect")
                    tasks.connect()

                if queue not in tasks.queues:
                    tasks.channel.queue_declare(queue=queue, passive=True)
                    tasks.queues.append(queue)

                if tasks.channel.basic_publish(exchange='',
                                               routing_key=queue,
                                               body=json.dumps({'event': event,
                                                                'args': args})):
                    success = True
                    break
                else:
                    raise Exception("failed publish")
            except:
                logging.error(traceback.format_exc())
                time.sleep(1)
        if success:
            logging.warning("send its ok!")
            return _id
        else:
            raise Exception("it has not been possible to the request to the queue")

# avoids having to import tasks
connect = tasks.connect
send_task = tasks.send_task
add_task = tasks.add_task
task = tasks.task
