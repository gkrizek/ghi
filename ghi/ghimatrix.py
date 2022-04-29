#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import logging

try:
    from nio import AsyncClient, LoginResponse
    from nio.responses import RoomResolveAliasError
except ImportError:
    pass


CRED_FILE = "ghi_matrix_credentials.json"


def createCreds(resp: LoginResponse, homeserver, matrixSecFile) -> None:
    """Writes the required login details to disk so we can log in later without
    using a password.

    Arguments:
        resp {LoginResponse} -- the successful client login response.
        homeserver -- URL of homeserver, e.g. "https://matrix.example.org"
    """
    # open the config file in write-mode
    with open(matrixSecFile, "w") as f:
        # write the login details to disk
        json.dump(
            {
                "homeserver": homeserver,
                "user_id": resp.user_id,
                "device_id": resp.device_id,
                "access_token": resp.access_token,
            },
            f,
        )


def sendMessages(*args, **kwargs) -> None:
    return asyncio.run(_sendMessages(*args, **kwargs))


async def _sendMessages(pool, messages) -> None:
    homeserver = pool.matrixServer
    user_id = pool.matrixUser
    password = pool.matrixPassword
    deviceName = pool.matrixDevId
    credPath = pool.matrixSecPath
    rooms = pool.matrixRooms

    matrixSecFile = os.path.join(credPath, CRED_FILE)
    # If there are no previously-saved credentials, we'll use the password
    if not os.path.exists(matrixSecFile):
        logging.info("First time use. Did not find credential file. Using info from config to create one.")

        if not (homeserver.startswith("https://") or homeserver.startswith("http://")):
            homeserver = "https://" + homeserver

        client = AsyncClient(homeserver, user_id)

        resp = await client.login(password, device_name=deviceName)

        # check that we logged in successfully
        if isinstance(resp, LoginResponse):
            createCreds(resp, homeserver, matrixSecFile)
        else:
            logging.info(f'homeserver = "{homeserver}"; user = "{user_id}"')
            logging.info(f"Failed to log in: {resp}")
            sys.exit(1)

        logging.info("Logged in using a password. Credentials were stored.")

        await client.close()

    with open(matrixSecFile, "r") as f:
        config = json.load(f)
        client = AsyncClient(config["homeserver"])

        client.access_token = config["access_token"]
        client.user_id = config["user_id"]
        client.device_id = config["device_id"]

        for room_id in rooms:
            await client.join(room_id)
            if room_id[0] != "!":
                response = await client.room_resolve_alias(room_id)

                if isinstance(response, RoomResolveAliasError):
                    logging.info(f"Error looking up alias for {room_id}: {response}")
                    return {
                        "statusCode": 500,
                        "body": json.dumps({
                            "success": False,
                            "message": "An error happened while sending messages to Matrix"
                        })
                    }

                room_id = response.room_id

            for message in messages:
                await client.room_send(
                    room_id,
                    message_type="m.room.message",
                    content={"msgtype": "m.text", "body": "", "format": "org.matrix.custom.html", "formatted_body":message},
                )

    await client.close()

    if len(messages) == 1:
        resultMessage = "Matrix - Successfully sent 1 message."
    else:
        resultMessage = "Matrix - Successfully sent {} messages.".format(len(messages))

    logging.info(resultMessage)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "message": resultMessage
        })
    }
