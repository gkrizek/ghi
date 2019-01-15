import json
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "../")
from irc import Colors


def Push(payload, poolRepos):
 
    ref  = payload["ref"]
    colors = Colors()
    if ref.startswith("refs/tags"):
        # Tag was pushed
        message = (
            "[{light_purple}{repo}{reset}] {gray}{user}{reset} pushed tag "
            "{dark_purple}{tag}{reset}: {blue}{underline}{compareUrl}{reset}"
        ).format(
            repo         = payload["repository"]["name"],
            user         = payload["pusher"]["name"],
            tag          = ref.split("/", maxsplit=2)[2],
            compareUrl   = payload["compare"],
            blue         = colors.dark_blue,
            gray         = colors.dark_gray,
            light_purple = colors.light_purple,
            dark_purple  = colors.dark_purple,
            underline    = colors.underline,
            reset        = colors.reset
        )

        return {
            "statusCode": 200,
            "messages": [message]
        }

    else:
        # Commits were pushed
        messages   = []
        commits    = payload["commits"]
        repo       = payload["repository"]["name"]
        fullName   = payload["repository"]["full_name"]
        user       = payload["pusher"]["name"]
        length     = len(commits)
        branch     = ref.split("/", maxsplit=2)[2]
        compareUrl = payload["compare"]

        # Check if the pool has allowed branches set.
        # If they do, make sure that this branch is included
        for poolRepo in poolRepos:
            if poolRepo == fullName:
                if poolRepo["branches"] is None:
                    break
                elif branch not in poolRepo["branches"]:
                    return {
                        "statusCode": 202,
                        "body": json.dumps({
                            "success": True,
                            "message": "Received branch '%s' for repo '%s', but no pool is configured for it." % (branch, fullName)
                        })
                    }
            

        # Summary Message
        messages.append(
            "[{light_purple}{repo}{reset}] {gray}{user}{reset} pushed {bold}{length}{reset} "
            "commit(s) to {dark_purple}{branch}{reset}: {blue}{underline}{compareUrl}{reset}".format(
                repo         = repo,
                user         = user,
                length       = length,
                branch       = branch,
                compareUrl   = compareUrl,
                blue         = colors.dark_blue,
                gray         = colors.light_gray,
                light_purple = colors.light_purple,
                dark_purple  = colors.dark_purple,
                underline    = colors.underline,
                bold         = colors.bold,
                reset        = colors.reset

            )
        )

        # First 3 individual commits
        num = 0
        for commit in commits:
            if num > 3:
                break
            # If commit message is longer than 75 characters, truncate.
            commitMessage = commit["message"]
            if len(commitMessage) > 75:
                commitMessage = commitMessage[0:74] + "..."

            messages.append(
                "{light_purple}{repo}{reset}/{dark_purple}{branch}{reset} {dark_gray}{shortCommit}{reset} {light_gray}{user}{reset}: {message}".format(
                    repo         = repo,
                    branch       = branch,
                    shortCommit  = commit["id"][0:7],
                    user         = user,
                    message      = commitMessage,
                    light_gray   = colors.light_gray,
                    dark_gray    = colors.dark_gray,
                    light_purple = colors.light_purple,
                    dark_purple  = colors.dark_purple,
                    reset        = colors.reset
                )
            )
            num += 1

        return {
            "statusCode": 200,
            "messages": messages
        }
