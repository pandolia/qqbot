# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import traceback

from qqbot.common import StartDaemonThread, Queue

def workAt(taskQueue):
    while True:
        try:
            func, args, kwargs = taskQueue.get(timeout=0.5)
        except Queue.Empty:
            pass
        else:
            # func(*args, **kwargs)
            try:
                func(*args, **kwargs)
            except SystemExit:
                raise
            except:
                traceback.print_exc()

class TaskLoop(object):
    def __init__(self):
        self.mainQueue = Queue.Queue()
        self.childQueues = {}    
    
    # Put a task into `mainQueue`, it will be executed in the main thread.
    # So all tasks you `Put` will be executed one after another. Means that
    # you can access the global data safely in these tasks.
    def Put(self, func, *args, **kwargs):
        self.mainQueue.put((func, args, kwargs))
    
    # Put a task into a child queue which with label `queueLabel`. It will be
    # executed in a child thread. Normally, it is a good idea to put an IO
    # task into a child queue, and when this task finishs his job, he put
    # a committing task with his result into the main queue.
    # At first, there is only one worker(thread) works on a child queue. You
    # can call `AddWorkerTo` to add workers(threads) to a child queue.
    def PutTo(self, queueLabel, func, *args, **kwargs):
        self.Put(self.putTo, queueLabel, func, args, kwargs)
    
    def putTo(self, queueLabel, func, args, kwargs):
        if queueLabel in self.childQueues:
            self.childQueues[queueLabel].put((func, args, kwargs))
        else:
            self.childQueues[queueLabel] = Queue.Queue()
            self.childQueues[queueLabel].put((func, args, kwargs))
            StartDaemonThread(workAt, self.childQueues[queueLabel])

    def AddWorkerTo(self, queueLabel, n):
        self.Put(self.addWorkerTo, queueLabel, n)
    
    def addWorkerTo(self, queueLabel, n):
        if queueLabel not in self.childQueues:
            self.childQueues[queueLabel] = Queue.Queue()
        for i in range(n):
            StartDaemonThread(workAt, self.childQueues[queueLabel])

    def Run(self):
        workAt(self.mainQueue)

mainLoop = TaskLoop()
MainLoop = mainLoop.Run
Put = mainLoop.Put
PutTo = mainLoop.PutTo
AddWorkerTo = mainLoop.AddWorkerTo
