import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
from configuration import loadConfiguration


def handler(event, context=None):
    # Ensure it"s a valid request
    if event and "body" in event and "headers" in event:

        pools = loadConfiguration()

        return {
            "statusCode": 401,
            "body": "Received: %s" % event
        }

    else:
        return {
            "statusCode": 400,
            "body": "bad event data"
        }