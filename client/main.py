import websocket
import json
import random
import threading
import time
import sys
from reactive import reactive, Model, execute
from controller import Controller, DOM


def consume():
    while execute:
        call = execute.pop()
        call()


class A(Model):
    objects = {}

    def __init__(self, id, x):
        super(A, self).__init__(id)
        self.x = x
        A.objects[id] = self

filter = {'x': {"$gt": 7, "$lt": 10}}


def hello(model):
    print 'model.x: ->', model.x

controllers = [Controller(key='x', filter=filter, node=DOM(id='container'), func=hello)]


def target(ws):
    while True:
        result = ws.recv()
        data = json.loads(result)
        print 'buscamos si ya tenemos el objeto con id', data['id']
        try:
            model = A.objects[data['id']]
            print 'encontrado'
        except KeyError:
            model = A(**data)
            print 'nuevo'
            for c in controllers:
                if c.pass_filter(data):
                    reactive(model)(c.func)

        if all([c.test(model, data) for c in controllers]):
            print 'eliminamos obj de cache'
            del A.objects[model.id]
        else:
            model.x = data['x']
        print A.objects
        print 'consume'
        consume()

if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.create_connection("ws://127.0.0.1:8888/ws")
    t = threading.Thread(target=target, args=(ws,))
    t.start()

    while True:
        if sys.argv[1] != 'NO':
            ws.send(json.dumps({'id': '0', 'x': random.randint(0, 10)}))
        time.sleep(1)

    ws.close()

