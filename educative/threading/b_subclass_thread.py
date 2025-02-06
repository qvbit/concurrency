from threading import Thread, current_thread


class MyTask(Thread):
    def __init__(self):
        Thread.__init__(self, name="subclassThread", args=(2, 3))

    def run(self):
        """This is the only method we can override"""
        print("{0} is executing".format(current_thread().name))


my_task = MyTask()

my_task.start()

my_task.join()

print("{0} exiting".format(current_thread().name))
