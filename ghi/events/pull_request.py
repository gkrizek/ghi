import json


def PullRequest(payload):

    action = payload["action"]

    if action in ["opened", "closed", "reopened"]:
        if action == "closed" and payload["pull_request"]["merged"]:
            action = "merged"

        message = "[{repo}] {user} {action} pull request #{number}: {title} ({baseBranch}...{headBranch}) {url}".format(
            repo       = payload["pull_request"]["base"]["repo"]["name"],
            user       = payload["pull_request"]["user"]["login"],
            action     = action,
            number     = payload["number"],
            title      = payload["pull_request"]["title"],
            baseBranch = payload["pull_request"]["base"]["ref"],
            headBranch = payload["pull_request"]["head"]["ref"],
            url        = payload["pull_request"]["url"]
        )

        return {
            "statusCode": 200,
            "messages": [message]
        }

    else:
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": "Pull Request Action was %s. Doing nothing." % action
            })
        }