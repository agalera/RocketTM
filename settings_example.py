ip = "localhost"
port = 5672
imports = ['examples.test1',
           'examples.test2']

queues = [{'name': 'rocket1', 'concurrency': 7},
          {'name': 'rocket2', 'concurrency': 1}]
