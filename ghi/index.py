import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import logging
from configuration import getConfiguration
from github import getPool, parsePayload
from irc import sendMessages
from validation import validatePayload
from __init__ import __version__


def handler(event, context=None):
    # ensure it's a valid request
    if event and "body" in event and "headers" in event:

        # AWS Lambda configures the logger before executing this script
        # We want to remove their configurations and set our own
        log = logging.getLogger()
        if log.handlers:
            for handler in log.handlers:
                log.removeHandler(handler)

        if "X-Ghi-Server" in event["headers"]:
            # was invoked by local server
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [ghi] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(message)s"
            )

        # By default ghi will respond to the request immediately,
        # then invoke itself to actually process the event.
        # This can be disabled by setting GHI_LONG_RESPONSE="true"
        if "requestContext" in event:
            from aws import InvokeSelf
            # Was invoked by AWS
            if "GHI_LONG_RESPONSE" in os.environ and os.getenv("GHI_LONG_RESPONSE"):
                pass
            elif "X-Ghi-Invoked" not in event["headers"]:
                return InvokeSelf(event)

        # validate and load configuration file
        configuration = getConfiguration()
        if configuration["statusCode"] != 200:
            return configuration

        # Enable debug if set in config
        if configuration["debug"]:
            logging.getLogger().setLevel(logging.DEBUG)

        # verify the request is from GitHub
        githubPayload = event["body"]

        # Enhanced logging if debug is set
        logging.debug("Ghi Version:")
        logging.debug(__version__)
        logging.debug("Payload:")
        logging.debug(githubPayload)
        logging.debug("Headers:")
        logging.debug(event["headers"])

        # figure out which pool this should belong to so we can use its secret
        pool = getPool(githubPayload, configuration["pools"])
        if pool["statusCode"] != 200:
            return pool

        try:
            if pool["verify"]:
                githubSignature = event["headers"]["X-Hub-Signature"]
            try:
                githubEvent = event["headers"]["X-GitHub-Event"]
            except KeyError as e:
                githubEvent = event["headers"]["X-Github-Event"]
        except KeyError as e:
            errorMessage = "missing header in request: %s" % e
            logging.error(errorMessage)
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": errorMessage
                })
            }

        # check signatures of request
        if pool["verify"]:
            validPayload = validatePayload(
                payload=githubPayload,
                signature=githubSignature,
                secret=pool["secret"]
            )
            if not validPayload:
                logging.error("GitHub payload validation failed")
                return {
                    "statusCode": 401,
                    "body": json.dumps({
                        "success": False,
                        "message": "payload validation failed"
                    })
                }
        else:
            logging.debug("Skipping payload verification because 'verify' set to False.")

        getMessages = parsePayload(githubEvent, githubPayload, pool["pool"].repos, pool["pool"].shorten)
        if getMessages["statusCode"] != 200:
            return getMessages

        logging.debug("Messages:")
        logging.debug(getMessages["messages"])
        
        # Send messages to the designated IRC channel(s)
        sendToIrc = sendMessages(pool["pool"], getMessages["messages"])
        if sendToIrc["statusCode"] != 200:
            return sendToIrc

        result = "Successfully notified IRC."
        logging.info(result)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": result
            })

        }

    else:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "message": "bad event data"
            })
        }