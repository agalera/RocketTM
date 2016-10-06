from rockettm import task
import time

@task('function2')
def function2(*args, **kwargs):
    for x in range(10):
        print(x)
        time.sleep(0.1)
    return True
