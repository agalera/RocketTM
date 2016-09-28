from rockettm import task
import time
import basicevents

@basicevents.subscribe('test')
def prueba():
    print("basicevents!")

@task('function4')
def function3(*args, **kwargs):
    basicevents.send('test')
    return True

