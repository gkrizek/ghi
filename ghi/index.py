import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import logging
from configuration import getConfiguration
from github import getPool, parsePayload
from irc import sendMessages
from ghilogging import setup_server_logging
from ghimastodon import sendToots
from validation import validatePayload
from __init__ import __version__


def handler(event, context=None, sysd=None):
    # ensure it's a valid request
    if event and "body" in event and "headers" in event:
        # validate and load configuration file
        configuration = getConfiguration()
        if configuration["statusCode"] != 200:
            return configuration

        # configure logging according to server-environment
        if sysd == "systemd":
            setup_server_logging("systemd", configuration["debug"])
        elif "X-Ghi-Server" in event["headers"]:
            setup_server_logging("plain", configuration["debug"])
        else:
            setup_server_logging("aws", configuration["debug"])

        # verify the request is from GitHub
        githubPayload = event["body"]

        # Enhanced logging if debug is set
        logging.debug("Ghi Version:")
        logging.debug(__version__)
        logging.debug("Payload:")
        logging.debug(githubPayload)
        logging.debug("Headers:")
        logging.debug(event["headers"])

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

        ircCheck = False
        mastCheck = False
        failure = False
        
        if "irc" in pool["pool"].outlets:
            logging.debug("IRC Messages:")
            logging.debug(getMessages["ircMessages"])

            # Send messages to the designated IRC channel(s)
            sendToIrc = sendMessages(pool["pool"], getMessages["ircMessages"])
            if sendToIrc["statusCode"] != 200:
                failure = True
                ircResult = "Something went wrong while trying to notify IRC."
            else:
                ircResult = "Successfully notified IRC."
                ircCheck = True
            logging.info(ircResult)
            

        githubPayload = json.loads(githubPayload)

        if githubEvent == "pull_request":
            if not (githubPayload["action"] == "closed" and githubPayload["pull_request"]["merged"]):
                mastAppliedMergeFilter = pool["pool"].mastMergeFilter
            else:
                mastAppliedMergeFilter = False
        else:
            mastAppliedMergeFilter = pool["pool"].mastMergeFilter

        if "mastodon" in pool["pool"].outlets and not mastAppliedMergeFilter:
            logging.debug("Mastodon Messages:")
            logging.debug(getMessages["mastMessages"])

            # Send messages to Mastodon's instance's user's timeline
            sendToMastodon = sendToots(pool["pool"], getMessages["mastMessages"])
            if sendToMastodon["statusCode"] != 200:
                failure = True
                mastResult = "Something went wrong while trying to notify Mastodon."
            else:
                mastResult = "Succesfully notified Mastodon."
                mastCheck = True
            logging.info(mastResult)
            
        if ircCheck or not mastAppliedMergeFilter and not failure:
            result = "Succesfully notified {both0}{IRC}{both1}{Mastodon}.".format(
                both0    = "both " if ircCheck and mastCheck else "",
                both1    = " and " if ircCheck and mastCheck else "",
                IRC      = "IRC" if ircCheck else "",
                Mastodon = "Mastodon" if mastCheck else ""
            )
            if "mastodon" in pool["pool"].outlets and mastAppliedMergeFilter:
                mastResult = "Didn't toot because of the merge filter."
                logging.info(mastResult)
                result = result[:-1] + ", but not Mastodon because of the merge filter."    
        elif "mastodon" in pool["pool"].outlets and mastAppliedMergeFilter:
            mastResult = "Event received, but didn't toot because of the merge filter."
            logging.info(mastResult)
            result = "Event received, but didn't toot because of the merge filter."

        if failure:
            result = "Something went wrong."
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "message": result
                })
            }
        else:        
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