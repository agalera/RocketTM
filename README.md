
[![PypiDownloads](https://img.shields.io/pypi/dm/rockettm.svg)](https://pypi.python.org/pypi/rockettm)
[![pythonversions](https://img.shields.io/pypi/pyversions/rockettm.svg)](https://pypi.python.org/pypi/rockettm)

# Rocket task manager
Server task manager in python

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

send_task("rocket1", "function1", "h", "o", "l", "a")

```

### Declare new task
```python
# task example
from rockettm import task


@task('function1')
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
