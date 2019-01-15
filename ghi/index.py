import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import logging
from configuration import getConfiguration
from github import getPool, parsePayload
from irc import sendMessages
from validation import validatePayload


def handler(event, context=None):
    # ensure it"s a valid request
    if event and "body" in event and "headers" in event:

        if "X-Ghi" in event["headers"]:
            # was invoked by local server
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [ghi] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        else:
            # was invoked in AWS
            logging.basicConfig(
                level=logging.INFO,
                format="%(message)s"
            )

        # validate and load configuration file
        configuration = getConfiguration()
        if configuration["statusCode"] != 200:
            return configuration

        # Enable debug if set in config
        if configuration['debug']:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(message)s"
            )

        # verify the request is from GtitHub
        githubPayload = event["body"]

        # Enhanced logging if debug is set
        logging.debug("Payload:")
        logging.debug(githubPayload)
        logging.debug("Headers:")
        logging.debug(event["headers"])

        try:
            githubSignature = event["headers"]["X-Hub-Signature"]
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

        # figure out which pool this should belong to so we can use its secret
        pool = getPool(githubPayload, configuration["pools"])
        if pool["statusCode"] != 200:
            return pool

        # check signatures of request
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

        getMessages = parsePayload(githubEvent, githubPayload, pool["pool"].repos)
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