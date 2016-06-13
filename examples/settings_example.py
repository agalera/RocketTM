ip = "localhost"
port = 5672

logger = {'filename': "rockettm.log",  # optional,
                                       # is not defined print in console
          'level': 20  # optional
          }

# search @task in imports
imports = ['examples.test1',
           'examples.test2',
           'examples.test3']

# support params
# name (mandatory), string
# concurrency (mandatory), int
# durable (optional), boolean
# max_time (in seconds) (optional), int

queues = [{'name': 'rocket1', 'durable': True, 'concurrency': 1},
          {'name': 'rocket2', 'concurrency': 1},
          {'name': 'rocket3', 'concurrency': 2, 'max_time': 1}]
