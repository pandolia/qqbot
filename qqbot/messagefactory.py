# -*- coding: utf-8 -*-

import Queue

from common import StartThread

class Message:    
    def __init__(self, mtype, **kw):
        self.mtype = mtype
        self.__dict__.update(kw)

# messages are generated in child threads, but be processed in the main thread.
# DO NOT call any method of the factory in generators, yield messages instead.
# DO NOT yield message in processors, just call methods of the factory instead.
class MessageFactory:
    def __init__(self):
        self.msgProcessors = {}
        self.msgQueue = Queue.Queue()
        
    def Run(self):
        while True:
            try:
                msg = self.msgQueue.get(timeout=0.5)
            except Queue.Empty:
                continue
            else:
                try:
                    self.Process(msg)
                except SystemExit as e:
                    self.onStop(e.code)
                    raise
    
    def Process(self, msg):
        if msg.mtype == 'stop':
            raise SystemExit(msg.code)
        elif msg.mtype == 'registerprocessor':
            self.msgProcessors[msg.ptype] = msg.processor            
        elif msg.mtype == 'addgenerator':
            StartThread(self.genLoop, msg.generator, daemon=True)
        elif msg.mtype in self.msgProcessors:
            self.msgProcessors[msg.mtype](self, msg)                
        else:
            raise Exception('Unregister message type: %s' % msg.mtype)
    
    def Stop(self, code=0):
        raise SystemExit(code)
    
    def onStop(self, code):
        print 'stop with', code
    
    def genLoop(self, generator):
        for msg in generator():
            self.msgQueue.put(msg)

    # you must register the processor for $mtype before you yield
    # any $mtype message, and before you add any generator which
    # may yield $mtype messages
    def RegisterProcessor(self, mtype, processor=None):
        if processor is None:
            def register(processor):
                self.msgProcessors[mtype] = processor
                return processor
            return register
        else:
            self.msgProcessors[mtype] = processor

    On = RegisterProcessor
    
    def AddGenerator(self, generator):
        self.msgQueue.put(Message('addgenerator', generator=generator))
        return generator
    
    Generator = AddGenerator
    
    def Put(self, msg):
        self.msgQueue.put(msg)

if __name__ == '__main__':
    import time
    
    prev = time.time()
    
    factory = MessageFactory()        
    
    # must register 'normal-message' processor before yield any 'normal-message' message,
    # and before add any producer which may yield 'normal-message' messages.
    @factory.On('normal-message')
    def processor(fac, msg):
        print 'Message%s: done' % msg.__dict__
    
    @factory.Generator
    def generator1():
        while True:
            time.sleep(0.2)
            yield Message('normal-message', pid=1)
    
    @factory.Generator
    def generator2():
        while True:
            time.sleep(0.2)
            yield Message('normal-message', pid=2)
    
    @factory.Generator
    def generator3():
        while True:
            time.sleep(0.2)
            if time.time() - prev >= 3:
                yield Message('stop', code=1)
            else:
                yield Message('normal-message', pid=3)
    
    factory.Run()
    
