import argparse
import json
import logging
import tornado.ioloop
import tornado.web
from index import handler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ghi] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def GetArgs():
    # Allow a configurable port
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", dest="port", help="Port to listen on", type=int, default=8888)
    parser.add_argument('--quick-response', dest='quickresponse', help="Reply to client immediately, then process event", action='store_true')
    args = parser.parse_args()
    return {
        "port": args.port,
        "response": args.quickresponse
    }


def CreatePayload(method, path, body, headers):
    # Create an payload that the index file will understand
    payload = {}
    payload["httpMethod"] = method
    payload["path"] = path
    payload["headers"] = headers
    payload["body"] = json.dumps(body)
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

        payload = CreatePayload(
            method=self.request.method,
            path=self.request.path,
            body=body,
            headers=headers
        )

        # Reply to the client immediately, then process event
        quickResponse = GetArgs()['response']
        if quickResponse:
            # Return first, then execute function
            self.set_status(200)
            self.finish('{"success": true,"message":"Request received."}')
            
            handler(payload)
        
        else:
            # Invoke the application
            requestResult = handler(payload)

            self.set_status(requestResult["statusCode"])
            self.finish(requestResult["body"])


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