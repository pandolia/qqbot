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
    
    def Put(self, func, *args, **kwargs):
        self.mainQueue.put((func, args, kwargs))
    
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
