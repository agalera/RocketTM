
[![PypiDownloads](https://img.shields.io/pypi/dm/rockettm.svg)](https://pypi.python.org/pypi/rockettm)
[![pythonversions](https://img.shields.io/pypi/pyversions/rockettm.svg)](https://pypi.python.org/pypi/rockettm)

# Rocket task manager
Asynchronous task manager in python

## Install

```bash
pip install rockettm
```

Link pypi: https://pypi.python.org/pypi/rockettm


## Example

### Send task
```python
# send task
from rockettm import send_task

send_task("queue_name", "name_task", "arg1", ["arg2", "2"], {'args': 3}, ('arg', 4))

```

### Declare new task
Warning! if there are 2 tasks registered with the same name, will run 2!

```python
# task example
from rockettm import task


@task('name_task')
def function1(*args, **kwargs):
    return True

```

### settings.py example
```python
# settings.py example
ip = "localhost"
port = 5672
imports = ['examples.test1',
           'examples.test2']

queues = [{'name': 'rocket1', 'concurrency': 7},
          {'name': 'rocket2', 'concurrency': 1}]

```

Run server
```bash
rabbitmq_server file_settings.py
```

## Documentation
### Functions
- task(name_task_event)

It is a decorator to create tasks


- send_task(queue, name_task, *args)

Send task


- add_task(name_task, func(object))

Add manual task

## TODO
- Support retrying
