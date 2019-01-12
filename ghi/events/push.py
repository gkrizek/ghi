

def Push(payload):

    ref  = payload["ref"]

    if ref.startswith("refs/tags"):
        # Tag was pushed
        message = "[{repo}] {user} pushed tag {tag}: {compareUrl}".format(
            repo       = payload["repository"]["name"],
            user       = payload["pusher"]["name"],
            tag        = ref.split("/", maxsplit=2)[2],
            compareUrl = payload["compare"]
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
        user       = payload["pusher"]["name"]
        length     = len(commits)
        branch     = ref.split("/", maxsplit=2)[2]
        compareUrl = payload["compare"]

        # Summary Message
        messages.append(
            "[{repo}] {user} pushed {length} commits to {branch}: {compareUrl}".format(
                repo       = repo,
                user       = user,
                length     = length,
                branch     = branch,
                compareUrl = compareUrl

            )
        )

        # Individual commits
        for commit in commits:
            # If commit message is longer than 75 characters, truncate.
            commitMessage = commit["message"]
            if len(commitMessage) > 75:
                commitMessage = commitMessage[0:74] + "..."

            messages.append(
                "{repo}/{branch} {shortCommit} {user}: {message}".format(
                    repo        = repo,
                    branch      = branch,
                    shortCommit = commit["id"][0:7],
                    user        = user,
                    message     = commitMessage
                )
            )

        return {
            "statusCode": 200,
            "messages": messages
        }
