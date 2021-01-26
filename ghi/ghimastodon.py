import os
import json
import logging

try:
    from mastodon import Mastodon
    from mastodon.Mastodon import MastodonUnauthorizedError, MastodonIllegalArgumentError
except ImportError:
    pass


def createCreds(pool):
    instance = pool.mastInstance
    user = pool.mastUser
    password = pool.mastPassword
    secPath = pool.mastSecPath
    appName = pool.mastAppName
    clientCredFile = os.path.join(secPath, "ghi_clientcred.secret")
    userCredFile = os.path.join(secPath, "ghi_usercred.secret")

    Mastodon.create_app(
        appName,
        api_base_url = instance,
        to_file = clientCredFile
    )

    mastodon = Mastodon(
        client_id = clientCredFile,
        api_base_url = instance
    )

    mastodon.log_in(
        user,
        password,
        to_file = userCredFile
    )
    

def login(pool):
    instance = pool.mastInstance
    user = pool.mastUser
    appName = pool.mastAppName
    secPath = pool.mastSecPath
    userCredFile = os.path.join(secPath, "ghi_usercred.secret")

    try:
        if os.path.isfile(userCredFile):
            mastodon = Mastodon(
                access_token = userCredFile,
                api_base_url = instance
            )
            mastodon.account_verify_credentials()
            logging.info("Mastodon - Connected to {instance} as user {user} with appname {appname}"
            .format(
                instance = instance,
                user = user,
                appname = appName
            ))
        else:
            logging.info("Mastodon - Creating credential-files.")
            createCreds(pool)
            return login(pool)
    except MastodonUnauthorizedError:
        notice = "Mastodon - Invalid user-credentials: recreating credential-files."
        logging.info(notice)
        createCreds(pool)
        return login(pool)
    return mastodon


def sendToots(pool, messages):
    try:
        mastodon = login(pool)
    except MastodonIllegalArgumentError as e:
        errorMessage = "Mastodon - Probably the password for Mastodon in the configfile is not correct"
        logging.error(errorMessage)
        logging.info(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": errorMessage
            })
        }

    try:
        for message in messages:
            mastodon.toot(message)
    except Exception as e:
        errorMessage = "Mastodon - There was a problem sending messages to Mastodon" 
        logging.error(errorMessage)
        logging.info(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": errorMessage
            })
        }

    if len(messages) == 1:
        resultMessage = "Mastodon - Successfully sent 1 toot."
    else:
        resultMessage = "Mastodon - Successfully sent {} toots.".format(len(messages))
        
    logging.info(resultMessage)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "message": resultMessage
        }) 
    }
