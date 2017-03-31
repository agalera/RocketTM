from rockettm import task
import time


@task('function3', 100)
def function3(*args, **kwargs):
    print("init sleep")
    for x in range(1000000000):
        pass
    print("end sleep")
    print("args", args)
    print("kwargs", kwargs)
    return True

