ip = "localhost"
port = 5672
imports = ['examples.test1',
           'examples.test2']

# support params
# name (mandatory), string
# concurrency (mandatory), int
# durable (optional), boolean

queues = [{'name': 'rocket1', 'durable': True, 'concurrency': 7},
          {'name': 'rocket2', 'concurrency': 1}]
