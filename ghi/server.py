import argparse
import json
import logging
import os
import queue
import signal
import sys
import threading
import tornado.ioloop
import tornado.web
import uuid
from time import sleep


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ghi] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

 
def GetArgs():
    # Allow a configurable port
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", dest="port", help="Port to listen on", type=int)
    args = parser.parse_args()
    if args.port:
        port = args.port
    elif "GHI_PORT" in os.environ:
        port = os.getenv("GHI_PORT")
    else:
        port = 7890
    return {
        "port": port
    }


def InvokeFunction(payload):
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    from index import handler
    return handler(payload)
    

def CreatePayload(method, path, requesterIp, body, headers):
    # Create a payload that the index file will understand
    payload = {}
    payload["httpMethod"] = method
    payload["path"] = path
    payload["requesterIp"] = requesterIp
    payload["headers"] = headers
    payload["body"] = body.decode("UTF-8")
    payload["uuid"] = str(uuid.uuid4())
    return payload


class TaskQueue(queue.Queue):


    def __init__(self, num_workers=1):
        queue.Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()


    def add_task(self, task, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))


    def start_workers(self):
        for each in range(self.num_workers):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()


    def worker(self):
        while True:
            item, args, kwargs = self.get()
            logging.info("Start UUID: %s" % args[0]['uuid'])
            logging.info("{} {} ({})".format(args[0]['httpMethod'], args[0]['path'], args[0]['requesterIp']))
            response = item(*args, **kwargs)
            logging.info("")
            logging.info("Response:")
            logging.info(response)
            logging.info("Stop UUID: %s" % args[0]['uuid'])
            logging.info("")
            self.task_done()
            sleep(0.5)


class MainHandler(tornado.web.RequestHandler):


    def initialize(self, taskQueue):
        self.taskQueue = taskQueue


    def post(self):
        # Parse Body
        if self.request.body:
            body = self.request.body
        else:
            self.set_status(400)
            self.finish("No body found")
            return

        # Parse Headers
        headers = {}
        for (k,v) in sorted(self.request.headers.get_all()):
            headers[k] = v
        headers["X-Ghi-Server"] = "true"

        payload = CreatePayload(
            method=self.request.method,
            path=self.request.path,
            requesterIp=self.request.remote_ip,
            body=body,
            headers=headers
        )

        self.taskQueue.add_task(InvokeFunction, payload)

        self.set_status(200)
        self.finish('{"success": true,"message":"Request received.","uuid":"%s"}' % payload["uuid"])


    def get(self):
        self.set_status(404)
        self.finish("Not Found")


def application():
    taskQueue = TaskQueue()
    return tornado.web.Application([
        (r"/.*", MainHandler, dict(taskQueue=taskQueue)),
    ])


def ShutDown(signum, frame):
    if signum:
        logging.debug("Received SIGTERM")
        logging.debug("Signum: " + str(signum))
    logging.info("server is shutting down")
    exit(0)


def main():
    try:
        # Handle logging ourselves
        logging.getLogger('tornado.access').disabled = True
        port = GetArgs()['port']
        app = application()
        app.listen(port)
        signal.signal(signal.SIGTERM, ShutDown)
        logging.info("server listening on %s" % port)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        ShutDown(None, None)


if __name__ == "__main__":
    main()