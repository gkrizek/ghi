import json
from events.pull_request import PullRequest
from events.push import Push


def findPool(repo, pools):
    ownerPool = None
    for pool in pools:
        if pool.containsRepo(repo):
            ownerPool = pool
            break
    return ownerPool


def parsePayload(event, payload, pools):

    # for every supported event find the pool, parse the payload, and return IRC messages
    if event == "push":
        # Find what pool is watching for this repo
        repo = payload["repository"]["full_name"]
        pool = findPool(repo, pools)
        if pool is None:
            return {
                "statusCode": 202,
                "body": json.dumps({
                    "success": True,
                    "message": "Received repository '%s', but no pool is configured for it." % repo
                })
            }

        # Create messages based on the payload
        push = Push(payload)
        if push["statusCode"] != 200:
            return push

        return {
            "statusCode": 200,
            "pool": pool,
            "messsages": push["messages"]
        }


    elif event == "pull_request":
        # Find what pool is watching for this repo
        repo = payload["repo"]["full_name"]
        pool = findPool(repo, pools)
        if pool is None:
            return {
                "statusCode": 202,
                "body": json.dumps({
                    "success": True,
                    "message": "Received repository '%s', but no pool is configured for it." % repo
                })
            }

        # Create messages based on the payload
        push = Push(payload)
        if push["statusCode"] != 200:
            return push

        return {
            "statusCode": 200,
            "pool": pool,
            "messsages": push["messages"]
        }

    else:
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": "Received event '%s'. Doing nothing..." % event
            })
        }