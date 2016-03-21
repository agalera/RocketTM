from __future__ import print_function
import pika
import json


class tasks(object):
    subs = {}
    logger = print
    conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = conn.channel()
    queues = []

    @staticmethod
    def add_task(event, func):
        tasks.logger(event)
        if event not in tasks.subs:
            tasks.subs[event] = []
        tasks.subs[event].append(func)

    @staticmethod
    def task(event):
        def wrap_function(func):
            tasks.add_task(event, func)
            return func
        return wrap_function

    @staticmethod
    def send_task(queue, event, *args):
        if queue not in tasks.queues:
            tasks.queues.append(queue)
            tasks.channel.queue_declare(queue=queue)
        tasks.channel.basic_publish(exchange='',
                                    routing_key=queue,
                                    body=json.dumps({'event': event,
                                                     'args': args}))

# avoids having to import tasks
send_task = tasks.send_task
add_task = tasks.add_task
task = tasks.task
