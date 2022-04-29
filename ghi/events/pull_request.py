import json
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
import github
from irc import Colors
from util import matrix_html


def PullRequest(payload, shorten):

    action = payload["action"]
    logging.info("Received action '%s'" % action)
    colors = Colors()
    if shorten:
        url = github.shortenUrl(payload["pull_request"]["html_url"])
    else:
        url = payload["pull_request"]["html_url"]

    if action in ["opened", "closed", "reopened"]:
        if action == "closed" and payload["pull_request"]["merged"]:
            action = "merged"

        ircMessage = (
            "[{light_purple}{repo}{reset}] {gray}{user}{reset} {bold}{action}{reset} pull request {bold}#{number}{reset}:"
            " {title} ({dark_purple}{baseBranch}{reset}...{dark_purple}{headBranch}{reset}) {blue}{underline}{url}{reset}\r\n"
        ).format(
            repo         = payload["pull_request"]["base"]["repo"]["name"],
            user         = payload["sender"]["login"],
            action       = action,
            number       = payload["number"],
            title        = payload["pull_request"]["title"],
            baseBranch   = payload["pull_request"]["base"]["ref"],
            headBranch   = payload["pull_request"]["head"]["ref"],
            url          = url,
            blue         = colors.dark_blue,
            gray         = colors.light_gray,
            light_purple = colors.light_purple,
            dark_purple  = colors.dark_purple,
            green        = colors.light_green,
            underline    = colors.underline,
            bold         = colors.bold,
            reset        = colors.reset
        )

        mastMessage = (
                "[{repo}] {action} PR from {user}: {title} {url}"
        ).format(
            repo   = payload["pull_request"]["base"]["repo"]["name"],
            action = action.capitalize(),
            user   = payload["pull_request"]["user"]["login"],
            title  = payload["pull_request"]["title"],
            url    = url
        )

        matrixMessage = (
            '[<font color="fuchsia">{repo}</font>] <font color="gray">{user}</font> <b>{action}</b> pull request <b>#{number}</b>: {title} '
            '(<font color="purple">{baseBranch}</font>...<font color="purple">{headBranch}</font>) <font color="navy"><u>{url}</u></font>'
        ).format(
            repo         = matrix_html(payload["pull_request"]["base"]["repo"]["name"]),
            user         = matrix_html(payload["sender"]["login"]),
            action       = matrix_html(action),
            number       = payload["number"],
            title        = matrix_html(payload["pull_request"]["title"]),
            baseBranch   = matrix_html(payload["pull_request"]["base"]["ref"]),
            headBranch   = matrix_html(payload["pull_request"]["head"]["ref"]),
            url          = url
        )

        return {
            "statusCode": 200,
            "ircMessages": [ircMessage],
            "mastMessages": [mastMessage],
            "matrixMessages": [matrixMessage]
        }

    else:
        message = "Pull Request Action was %s. Doing nothing." % action
        logging.info(message)
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": message
            })
        }
