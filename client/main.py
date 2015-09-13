import websocket
import json
import random
import threading
import time
import sys
from reactive import reactive, Model, execute


def consume():
    while execute:
        call = execute.pop()
        call()

class A(Model):
    def __init__(self):
        super(A, self).__init__()
        self.x = 0

obj = A()

@reactive
def hello():
    if obj.x == 9:
        print 'hello'
    else:
        print ':)'

def target(ws):
    while True:
        result = ws.recv()
        data = json.loads(result)
        obj.x = data['x']
        print data
        consume()

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.create_connection("ws://127.0.0.1:8888/ws")
    t = threading.Thread(target=target, args=(ws,))
    t.start()

    while True:
        if sys.argv[1] != 'NO':
            ws.send(json.dumps({'id': '0', 'x': random.randint(0, 10)}))
        time.sleep(1)

    ws.close()

