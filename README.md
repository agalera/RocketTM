
[![pythonversions](https://img.shields.io/pypi/pyversions/rockettm.svg)](https://pypi.python.org/pypi/rockettm)

# Rocket task manager
Asynchronous task manager in python

## Install

```bash
pip install rockettm
```

Link pypi: https://pypi.python.org/pypi/rockettm


## Example

### Rabbitmq not is localhost
```python
from rockettm import connect

# to run it, reconnect to RabbitMQ
connect("other_ip_or_domain")

```

### Configure logger in client
Using standard logger in python
https://docs.python.org/2/library/logging.html#logging.basicConfig

```python
import logging
from rockettm import send_task

# 50 CRITICAL, 40 ERROR, 30 WARNING, 20 INFO, 10 DEBUG, 0 NOTSET
logging.basicConfig(level=20)
send_task("queue_name", "name_task", "Pepito")

```

### Configure logger in server
in settings.py:

```python
# filename (DEFAULT "rockettm.log")
# level (DEFAULT 30)
# 50 CRITICAL, 40 ERROR, 30 WARNING, 20 INFO, 10 DEBUG, 0 NOTSET
logger = {'filename': "rockettm.log",  # optional,
                                       # is not defined print in console
          'level': 10  # optional
         }
```

### Send task
```python
# send task
from rockettm import send_task

send_task("queue_name", "name_task", "arg1", ["arg2", "2"], {'args': 3}, ('arg', 4), example="ok")

```

### Declare new task
Warning! if there are 2 tasks registered with the same name, will run 2!

```python
# task example
from rockettm import task


@task('name_task')
def function1(*args, **kwargs):
    return True

# max_time(timeout in seconds) example
@task('name_task2', max_time=10)
def long_call(*args, **kwargs):
    return True

```

### settings.py example
```python
# settings.py example
ip = "localhost"
port = 5672

logger = {'filename': "rockettm.log",  # optional,
                                       # is not defined print in console
          'level': 10  # optional
          }

# search @task in imports
imports = ['examples.test1',
           'examples.test2']

# support params
# name (mandatory), string
# concurrency (mandatory), int
# durable (optional), boolean
# max_time (in seconds) (optional), int
queues = [{'name': 'rocket1', 'durable': True, 'concurrency': 7},
          {'name': 'rocket2', 'concurrency': 1},
          {'name': 'rocket3', 'concurrency': 1, 'max_time': 10}]

```

Run server
```bash
rockettm_server file_settings.py
```

## Documentation
### Functions
- task(name_task_event)

It is a decorator to create tasks


- send_task(queue, name_task, *args)

Send task


- add_task(name_task, func(object))

Add manual task


- connect(ip_or_domain)

connects to another server other than localhost

## Basicevents

rockettm currently used basicevents for noticificaciones the api. You can use basicevents as its official documentation *

* Do not need to run (), rockettm up a common process for all workers

https://github.com/kianxineki/basicevents

