from rockettm import task
import time

@task('function2')
def function2(*args, **kwargs):
    for x in range(60):
        print(x)
        time.sleep(1)
    return True
