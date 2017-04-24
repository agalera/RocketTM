class RedisQueue(object):
    """Simple Queue with Redis Backend"""

    def __init__(self, redis, name='default', namespace='queue',
                 serializer='json'):
        self.__db = redis
        self.namespace = namespace
        self.name = name

        if serializer == 'pickle':
            import pickle as serializer
        else:
            import ujson as serializer

        self.serializer = serializer

    def gen_key(self, name=None, namespace=None):
        return '%s:%s' % (namespace or self.namespace, name or self.name)

    def qsize(self, name=None, namespace=None):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.gen_key(name, namespace))

    def empty(self, name=None, namespace=None):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize(name) == 0

    def put(self, item, name=None, namespace=None):
        """Put item into the queue."""
        self.__db.rpush(self.gen_key(name, namespace),
                        self.serializer.dumps(item))

    def get(self, name=None, namespace=None, block=True, timeout=None):
        """ Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        key = self.gen_key(name, namespace)
        if block:
            item = self.__db.blpop(key, timeout=timeout)
        else:
            item = self.__db.lpop(key)

        if item:
            item = self.serializer.loads(item[1])
        return item

    def get_nowait(self, name=None, namespace=None):
        """Equivalent to get(False)."""
        return self.get(name=name, namespace=namespace, block=False)
