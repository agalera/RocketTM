from pika import BlockingConnection, ConnectionParameters
import json
import logging


class tasks(object):
    subs = {}
    queues = []
    ip = "localhost"
    conn = False
    channel = False

    @staticmethod
    def connect(ip=None):
        logging.info("rabbitmq connect %s" % tasks.ip)
        if ip:
            tasks.ip = ip
        tasks.conn = BlockingConnection(ConnectionParameters(tasks.ip))
        tasks.channel = tasks.conn.channel()

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
        logging.info("send task to queue %s, event %s" % (queue, event))
        if not tasks.channel or tasks.channel.is_closed:
            tasks.connect()
        if queue not in tasks.queues:
            try:
                tasks.channel.queue_declare(queue=queue, passive=True)
                tasks.queues.append(queue)
            except:
                error = "Queue not declare, first start the server"
                logging.error(error)
                raise Exception(error)

        tasks.channel.basic_publish(exchange='',
                                    routing_key=queue,
                                    body=json.dumps({'event': event,
                                                     'args': args}))

# avoids having to import tasks
connect = tasks.connect
send_task = tasks.send_task
add_task = tasks.add_task
task = tasks.task
