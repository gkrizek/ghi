import json
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "../")
import github
from irc import Colors
from util import matrix_html


def Push(payload, poolRepos, shorten):
 
    ref  = payload["ref"]

    if payload["deleted"] and not payload["created"]:
        action = "deleted"
    elif payload["forced"]:
        action = "force pushed"
    else:
        action = "pushed"

    if shorten:
        url = github.shortenUrl(payload["compare"])
    else:
        url = payload["compare"]

    logging.info("Received ref '%s'" % ref)
    colors = Colors()
    if ref.startswith("refs/tags"):
        # Tag was pushed
        ircMessage = (
            "[{light_purple}{repo}{reset}] {gray}{user}{reset} {action} tag "
            "{dark_purple}{tag}{reset}: {blue}{underline}{compareUrl}{reset}\r\n"
        ).format(
            repo         = payload["repository"]["name"],
            user         = payload["pusher"]["name"],
            action       = action,
            tag          = ref.split("/", maxsplit=2)[2],
            compareUrl   = url,
            blue         = colors.dark_blue,
            gray         = colors.dark_gray,
            light_purple = colors.light_purple,
            dark_purple  = colors.dark_purple,
            underline    = colors.underline,
            reset        = colors.reset
        )

        mastMessage = (
            "[{repo}] {user} {action} tag {tag}: {compareUrl}"
        ).format(
            repo       = payload["repository"]["name"],
            user       = payload["pusher"]["name"],
            action     = action,
            tag        = ref.split("/", maxsplit=2)[2],
            compareUrl = url
        )

        matrixMessage = (
            '[<font color="fuchsia">{repo}</font>] <font color="gray">{user}</font> {action} '
            'tag <font color="purple">{tag}</font>: <font color="navy"><u>{compareUrl}</u></font>'
        ).format(
            repo         = matrix_html(payload["repository"]["name"]),
            user         = matrix_html(payload["pusher"]["name"]),
            action       = matrix_html(action),
            tag          = matrix_html(ref.split("/", maxsplit=2)[2]),
            compareUrl   = url
        )

        return {
            "statusCode": 200,
            "ircMessages": [ircMessage],
            "mastMessages": [mastMessage],
            "matrixMessages": [matrixMessage]
        }

    else:
        # Commits were pushed
        ircMessages    = []
        mastMessages   = []
        matrixMessages = []
        commits        = payload["commits"]
        repo           = payload["repository"]["name"]
        fullName       = payload["repository"]["full_name"]
        user           = payload["pusher"]["name"]
        length         = len(commits)
        branch         = ref.split("/", maxsplit=2)[2]

        # Check if the pool has allowed branches set.
        # If they do, make sure that this branch is included
        for poolRepo in poolRepos:
            if poolRepo["name"] == fullName:
                if poolRepo["branches"] is None:
                    break
                elif branch not in poolRepo["branches"]:
                    message = "Received branch '%s' for repo '%s', but no pool is configured for it." % (branch, fullName)
                    logging.info(message)
                    return {
                        "statusCode": 202,
                        "body": json.dumps({
                            "success": True,
                            "message": message
                        })
                    }
            

        # Summary Message
        if len(commits) > 1:
            plural = "s"
        else:
            plural = ""

        ircCommitInfo = ""
        if action != "deleted":
            ircCommitInfo = "{bold}{length}{reset} commit{plural} to ".format(
                bold   = colors.bold,
                reset  = colors.reset,
                length = length,
                plural = plural
            )

        ircMessages.append("[{light_purple}{repo}{reset}] {gray}{user}{reset} {action} {commitInfo}"
                           "{dark_purple}{branch}{reset}: {blue}{underline}{compareUrl}{reset}\r\n".format(
                repo         = repo,
                user         = user,
                action       = action,
                branch       = branch,
                compareUrl   = url,
                commitInfo   = ircCommitInfo,
                blue         = colors.dark_blue,
                gray         = colors.light_gray,
                light_purple = colors.light_purple,
                dark_purple  = colors.dark_purple,
                underline    = colors.underline,
                bold         = colors.bold,
                reset        = colors.reset

            )
        )

        mastCommitInfo = ""
        if action != "deleted":
            mastCommitInfo = "{length} commit{plural} to ".format(
                bold   = colors.bold,
                reset  = colors.reset,
                length = length,
                plural = plural
            )

        mastMessages.append(
            "[{repo}] {user} {action} {commitInfo}{branch}: {compareUrl}".format(
                repo       = repo,
                user       = user,
                action     = action,
                commitInfo = mastCommitInfo,
                branch     = branch,
                compareUrl = url
            )
        )

        matrixMessages.append(
            '[<font color="fuchsia">{repo}</font>] <font color="gray">{user}</font> {action} '
            '<b>{length}</b> commit{plural} to <font color="purple">{branch}</font>: '
            '<font color="navy"><u>{compareUrl}</u></font>'.format(
                repo         = matrix_html(repo),
                user         = matrix_html(user),
                action       = matrix_html(action),
                length       = length,
                branch       = matrix_html(branch),
                compareUrl   = url,
                plural       = matrix_html(plural)
            )
        )

        # First 3 individual commits
        num = 0
        for commit in commits:
            if num > 2:
                break
            # We're only interested in the first line of the commit message, the title.
            # If it is longer than 75 characters, truncate.
            commitMessage = commit["message"].split('\n', 1)[0]
            author = commit["author"]["name"]
            if len(commitMessage) > 75:
                commitMessage = commitMessage[0:74] + "..."

            ircMessages.append(
                "{light_purple}{repo}{reset}/{dark_purple}{branch}{reset} {dark_gray}{shortCommit}{reset} {light_gray}{user}{reset}: {message}\r\n".format(
                    repo         = repo,
                    branch       = branch,
                    shortCommit  = commit["id"][0:7],
                    user         = author,
                    message      = commitMessage,
                    light_gray   = colors.light_gray,
                    dark_gray    = colors.dark_gray,
                    light_purple = colors.light_purple,
                    dark_purple  = colors.dark_purple,
                    reset        = colors.reset
                )
            )

            mastMessages.append(
                "{repo}/{branch} {shortCommit} {user}: {message}".format(
                    repo        = repo,
                    branch      = branch,
                    shortCommit = commit["id"][0:7],
                    user        = author,
                    message     = commitMessage
                )
            )

            matrixMessages.append(
                '<font color="fuchsia">{repo}</font>/<font color="purple">{branch}</font> '
                '<font color="gray">{shortCommit}</font> <font color="lightgrey">{user}</font>: {message}'.format(
                    repo         = repo,
                    branch       = branch,
                    shortCommit  = commit["id"][0:7],
                    user         = author,
                    message      = commitMessage
                )
            )

            num += 1

        return {
            "statusCode": 200,
            "ircMessages": ircMessages,
            "mastMessages": mastMessages,
            "matrixMessages": matrixMessages
        }
