from rockettm import task
import time

@task('function2')
def function2(*args, **kwargs):
    print("recv")
    time.sleep(10*60)
    print("finish")
    return True
