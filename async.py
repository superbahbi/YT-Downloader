import time

from gevent import monkey; monkey.patch_all()
import bottle
from gevent import Greenlet
from gevent import pywsgi
from gevent import queue
import gevent

def worker(body):
    print 'worker called'
    data = [ 'one', 'two', 'three', 'four' ]
    for d in data:
        body.put(d)
        gevent.sleep(5)
    body.put(StopIteration)
def worker2(body):
    print 'worker2 called'
    data = [ 'five', 'six', 'seven', 'eight' ]
    for d in data:
        body.put(d)
        gevent.sleep(5)
    body.put(StopIteration)

@bottle.route('/')
def def1():
    body = gevent.queue.Queue()
    g = Greenlet.spawn(worker, body)
    return body
@bottle.route('/2')
def def1():
    body = gevent.queue.Queue()
    g = Greenlet.spawn(worker2, body)
    return body
def main():
    bottle.run(host='0',port=8081, server="gevent")

if __name__ == '__main__':
    main()