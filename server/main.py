from tornado import websocket, web, ioloop, gen
from tornado.queues import Queue
from tornado.ioloop import IOLoop
import json

import sys
sys.path.insert(0, '..')
from lib.filter_mongo import pass_filter

q = Queue()
q_out = Queue()
filters = []

mongo_model = {'id': '0', 'x': 50}

@gen.coroutine
def sender():
    while True:
        item = yield q_out.get()
        client = item[0]
        model = item[1]
        client.write_message(json.dumps(model))
        q_out.task_done()


@gen.coroutine
def consumer():
    global mongo_model
    while True:
        model = yield q.get()
        print 'get model id:', model['id']
        model_before = mongo_model
        print 'update model'
        mongo_model = model
        for client, filt in filters:
            print('filter:', filt)
            before = pass_filter(filt, model_before)
            print 'before:', before

            if not before:
                after = pass_filter(filt, model)
                print 'after:', after
                if after:
                    print 'send', client, model
                    yield q_out.put((client, model))
            else:
                print 'send', client, model
                yield q_out.put((client, model))
        q.task_done()


class SocketHandler(websocket.WebSocketHandler):
    def open(self):
        filters.append((self, {'x': {"$gt": 7, "$lt": 10}}))

    @gen.coroutine
    def on_message(self, message):
        print('***', message)
        yield q.put(json.loads(message))


app = web.Application([
    (r'/ws', SocketHandler),
])

if __name__ == '__main__':
    app.listen(8888)
    IOLoop.current().spawn_callback(consumer)
    IOLoop.current().spawn_callback(sender)
    ioloop.IOLoop.instance().start()
