import json
from events.pull_request import PullRequest
from events.push import Push


def getPool(payload, pools):
    ownerPool = None
    payload = json.loads(payload)
    repo = payload["repository"]["full_name"]

    for pool in pools:
        if pool.containsRepo(repo):
            ownerPool = pool
            break

    if ownerPool is None:
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": "Received repository '%s', but no pool is configured for it." % repo
            })
        }
    else:
        # get the secret for this repo
        for requestedRepo in ownerPool.repos:
            if repo == requestedRepo["name"]:
                repoName = requestedRepo["name"]
                repoSecret = requestedRepo["secret"]
        return {
            "statusCode": 200,
            "pool": ownerPool,
            "name": repoName,
            "secret": repoSecret
        }


def parsePayload(event, payload, repos):

    # for every supported event: find the pool, parse the payload, and return IRC messages
    payload = json.loads(payload)
    if event == "push":
        # Create messages based on the payload
        push = Push(payload, repos)
        if push["statusCode"] != 200:
            return push

        return {
            "statusCode": 200,
            "messages": push["messages"]
        }


    elif event == "pull_request":
        # Create messages based on the payload
        pullRequest = PullRequest(payload)
        if pullRequest["statusCode"] != 200:
            return pullRequest

        return {
            "statusCode": 200,
            "messages": pullRequest["messages"]
        }

    else:
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": "Received event '%s'. Doing nothing." % event
            })
        }