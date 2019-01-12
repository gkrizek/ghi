import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
from configuration import getConfiguration
from github import getPool, parsePayload
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
        pool = getPool(githubPayload, configuration['pools'])
        if pool['statusCode'] != 200:
            return pool

        # check signatures of request
        validPayload = validatePayload(
            payload=githubPayload,
            signature=githubSignature,
            secret=pool['secret']
        )
        if not validPayload:
            return {
                "statusCode": 401,
                "body": json.dumps({
                    "success": False,
                    "message": "payload validation failed"
                })
            }
  
        githubResult = parsePayload(githubEvent, githubPayload)
        if githubResult["statusCode"] != 200:
            return githubResult


        print(githubResult)
        
        return {
            "statusCode": 200,
            "body": "it worked"
        }



        """
        githubResult = {
            "statusCode": 200,
            "messages": [
                "message1",
                "message2"
            ]
        }
        pool = {
            "statusCode": 200,
            "pool": Pool Object,
            "name": "gkrizek/pipeline",
            "secret": "Abc123"
        }
        """
        # Create an IRC send function that will send the messages to the correct IRC channels
        

    else:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "message": "bad event data"
            })
        }