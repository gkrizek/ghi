import argparse
import json
import logging
import os
import sys
import tornado.ioloop
import tornado.web
import uuid
from index import handler
from tornado.process import Subprocess
from tornado import gen


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
        port = 8888
    return {
        "port": port
    }


@gen.coroutine
def InvokeFunction(payload):
    python = sys.executable
    if __file__.startswith('ghi'):
        index = 'ghi.index'
    else:
        index = 'index'

    command = (
        "{python} -c '"
        "from {index} import handler;print(handler({payload}))'"
    ).format(
        python=python,
        index=index,
        payload=json.dumps(payload)
    )
    process = Subprocess([command], stdout=Subprocess.STREAM, stderr=Subprocess.STREAM, shell=True)
    response, logs = yield [process.stdout.read_until_close(),process.stderr.read_until_close()]
    logging.info("Start UUID: %s" % payload["uuid"])
    logging.info("Response:")
    logging.info(response.decode("UTF-8").strip())
    logging.info("Logs:")
    for log in logs.decode("UTF-8").splitlines():
        logging.info(log)
    logging.info("Stop UUID: %s" % payload["uuid"])
    logging.info("")
    

def CreatePayload(method, path, body, headers):
    # Create an payload that the index file will understand
    payload = {}
    payload["httpMethod"] = method
    payload["path"] = path
    payload["headers"] = headers
    payload["body"] = json.dumps(body)
    payload["uuid"] = str(uuid.uuid4())
    return payload


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        # Parse Body
        if self.request.body:
            try:
                body = json.loads(self.request.body)
            except json.JSONDecodeError as e:
                self.set_status(400)
                self.finish("Problem parsing body:\n%s" % e)
                return
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
            body=body,
            headers=headers
        )

        logging.info("UUID: %s" % payload["uuid"])

        InvokeFunction(payload)

        self.set_status(200)
        self.finish('{"success": true,"message":"Request received.","uuid":"%s"}' % payload["uuid"])

    def get(self):
        self.set_status(404)
        self.finish("Not Found")

def application():
    return tornado.web.Application([
        (r"/.*", MainHandler),
    ])

if __name__ == "__main__":
    try:
        port = GetArgs()['port']
        app = application()
        app.listen(port)
        logging.info("server listening on %s" % port)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info("server is shutting down")