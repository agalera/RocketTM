from rockettm import task
import time

@task('function3', 5)
def function3(*args, **kwargs):
    print("init sleep")
    time.sleep(10)
    print("end sleep")
    print("args", args)
    print("kwargs", kwargs)
    return True

