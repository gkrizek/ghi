import json
import logging
import requests
from events.pull_request import PullRequest
from events.push import Push


def getPool(payload, pools):

    try:
        payload = json.loads(payload)
    except json.JSONDecodeError as e:
        message = "There was a problem parsing payload: %s" % e
        logging.error(message)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "message": message
            })
        }
    ownerPool = None
    repo = payload["repository"]["full_name"]

    for pool in pools:
        if pool.containsRepo(repo):
            ownerPool = pool
            break

    if ownerPool is None:
        message = "Received repository '%s', but no pool is configured for it." % repo
        logging.info(message)
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": message
            })
        }
    else:
        # get the secret for this repo
        for requestedRepo in ownerPool.repos:
            if repo == requestedRepo["name"]:
                repoName = requestedRepo["name"]
                repoSecret = requestedRepo["secret"]
                repoVerify = requestedRepo["verify"]
        logging.info("Matched repo '{}' to pool '{}'".format(repoName,ownerPool.name))
        return {
            "statusCode": 200,
            "pool": ownerPool,
            "name": repoName,
            "secret": repoSecret,
            "verify": repoVerify
        }


def shortenUrl(longUrl):
    gitIo = "https://git.io/create?url={}".format(longUrl)
    try:
        code = requests.post(gitIo)
        logging.debug(code.text)
        if code.status_code == 200:
            result = "https://git.io/{}".format(code.text)
        else:
            result = longUrl
    except Exception:
        result = longUrl
    return result


def parsePayload(event, payload, repos, shorten):

    # for every supported event: find the pool, parse the payload, and return IRC messages
    payload = json.loads(payload)
    logging.info("Received the '%s' event" % event)
    if event == "push":
        # Create messages based on the payload
        push = Push(payload, repos, shorten)
        if push["statusCode"] != 200:
            return push

        return {
            "statusCode": 200,
            "ircMessages": push["ircMessages"],
            "mastMessages": push["mastMessages"],
            "matrixMessages": push["matrixMessages"]
        }


    elif event == "pull_request":
        # Create messages based on the payload
        pullRequest = PullRequest(payload, shorten)
        if pullRequest["statusCode"] != 200:
            return pullRequest

        return {
            "statusCode": 200,
            "ircMessages": pullRequest["ircMessages"],
            "mastMessages": pullRequest["mastMessages"],
            "matrixMessages": pullRequest["matrixMessages"]
        }


    elif event == "ping":
        logging.info("Sent 'pong'")
        return {
            "statusCode": 202,
            "messages": "pong"
        }


    else:
        message = "Received event '%s'. Doing nothing." % event
        logging.info(message)
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": message
            })
        }