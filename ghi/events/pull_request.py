import json
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "../")
from irc import Colors


def PullRequest(payload):

    action = payload["action"]
    colors = Colors()
    if action in ["opened", "closed", "reopened"]:
        if action == "closed" and payload["pull_request"]["merged"]:
            action = "merged"

        message = (
            "{purple}[{repo}]{reset} {gray}{user}{reset} {bold}{action}{reset} pull request {green}#{number}{reset}:"
            " {title} ({baseBranch}...{headBranch}) {blue}{underline}{url}{reset}"
        ).format(
            repo       = payload["pull_request"]["base"]["repo"]["name"],
            user       = payload["pull_request"]["user"]["login"],
            action     = action,
            number     = payload["number"],
            title      = payload["pull_request"]["title"],
            baseBranch = payload["pull_request"]["base"]["ref"],
            headBranch = payload["pull_request"]["head"]["ref"],
            url        = payload["pull_request"]["url"],
            blue       = colors.dark_blue,
            gray       = colors.light_gray,
            purple     = colors.light_purple,
            green      = colors.light_green,
            underline  = colors.underline,
            bold       = colors.bold,
            reset      = colors.reset
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