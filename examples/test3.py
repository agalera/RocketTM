from rockettm import task


@task('function3', 5)
def function2(*args, **kwargs):
    print "args", args
    print "kwargs", kwargs
    return True

