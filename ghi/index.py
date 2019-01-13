import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
from configuration import getConfiguration
from github import getPool, parsePayload
from irc import sendMessages
from validation import validatePayload


def handler(event, context=None):
    # ensure it"s a valid request
    if event and "body" in event and "headers" in event:

        # validate and load configuration file
        configuration = getConfiguration()
        if configuration["statusCode"] != 200:
            return configuration

        # verify the request is from GtitHub
        githubPayload = event["body"]
        try:
            githubSignature = event["headers"]["X-Hub-Signature"]
            githubEvent = event["headers"]["X-GitHub-Event"]
        except KeyError as e:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "missing header in request: %s" % e
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
            return {
                "statusCode": 401,
                "body": json.dumps({
                    "success": False,
                    "message": "payload validation failed"
                })
            }

        githubResult = parsePayload(githubEvent, githubPayload, pool["pool"].repos)
        if githubResult["statusCode"] != 200:
            return githubResult

        # Send messages to the designated IRC channel(s)
        sendToIrc = sendMessages(pool["pool"], githubResult["messages"])
        if sendToIrc["statusCode"] != 200:
            return sendToIrc

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": "Successfully notified IRC."
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