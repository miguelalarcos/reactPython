from tornado import websocket, web, ioloop, gen
from tornado.queues import Queue
from tornado.ioloop import IOLoop
import json


def pass_filter(filter, model):
    for key, value in filter.items():
        if type(value) == int or type(value) == str:
            if model[key] != value:
                return False
        else:
            for op, val in value.items():
                if op == '$gt':
                    if model[key] <= val:
                        return False
                elif op == '$lt':
                    if model[key] > val:
                        return False
    return True

q = Queue()
q_out = Queue()
filters = []

@gen.coroutine
def sender():
    while True:
        item = yield q_out.get()
        client = item[0]
        model = item[1]
        client.write_message(json.dumps(model))
        q_out.task_done()
        #try:
        #    client.write_message(json.dumps(model))
        #    yield gen.sleep(0.01)
        #finally:
        #    q_out.task_done()


@gen.coroutine
def consumer():
    while True:
        model = yield q.get()
        print 'get model id:', model['id']
        model_before = {'id': '0', 'x': 50}
        print 'update model'
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
