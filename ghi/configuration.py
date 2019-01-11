import logging
import os
import yaml


class Pool(object):

    def __init__(self, name, repos, secret, host, port, nick, password, channels):
        self.name = name
        self.repos = repos
        self.secret = secret
        self.host = host
        self.port = port
        self.nick = nick
        self.password = password
        self.channels = channels


def readFile(path):
    configFile = open(path, "r")
    return configFile.read()


def loadConfiguration():

    # Read configuarion file
    # Looks first in os.getcwd, then ~/, then /tmp
    if os.path.exists("%s/.ghi.yml" % os.getcwd()):
        configFilePath = "%s/.ghi.yml" % os.getcwd()

    elif os.path.exists("%s/.ghi.yaml" % os.getcwd()):
        configFilePath = "%s/.ghi.yaml" % os.getcwd()

    elif os.path.exists(os.path.expanduser("~/.ghi.yml")):
        configFilePath = os.path.expanduser("~/.ghi.yml")

    elif os.path.exists(os.path.expanduser("~/.ghi.yaml")):
        configFilePath = os.path.expanduser("~/.ghi.yaml")

    elif os.path.exists("/tmp/.ghi.yml"):
        configFilePath = "/tmp/.ghi.yml"

    elif os.path.exists("/tmp/.ghi.yaml"):
        configFilePath = "/tmp/.ghi.yaml"

    else:
        return {
            "statusCode": 500,
            "body": {
                "success": False,
                "message": "Unable to find .ghi.yml file."
            }
        }

    try:
        logging.info("Found configuration file at '%s'" % configFilePath)
        config = yaml.load(readFile(configFilePath))
    except yaml.YAMLError as e:
        logging.error("There was a problem parsing configuation file.")
        logging.error(e)
        return {
            "statusCode": 500,
            "body": {
                "success": False,
                "message": "Error parsing yaml file:\n%s" % e
            }
        }

    # Validate top level params
    try:
        configVersion = config['version']
        if type(configVersion) is not int:
            raise TypeError("'version' is not an integer")

        configPools = config['pools']
        if type(configPools) is not list:
            raise TypeError("'pools' is not a list")

    except (KeyError, TypeError) as e:
        return {
            "statusCode": 500,
            "body": {
                "success": False,
                "message": "Missing or invalid parameter in configuration file: %s" % e
            }
        }

    # for each pool, validate and create a Pool object. append to array
    pools = []
    for pool in configPools:
        # Configuration Validation
        try:
            name = pool['name']
            if type(name) is not str:
                raise TypeError("'name' is not a string")

            repos = pool['github']['repos']
            if type(repos) is not list:
                raise TypeError("'repos' is not a list")

            if "GHI_GITHUB_SECRET" in os.environ:
                secret = os.environ["GHI_GITHUB_SECRET"]
            else:
                secret = pool['github']['secret']
            if type(secret) is not str:
                raise TypeError("'secret' is not a string")

            host = pool['irc']['host']
            if type(host) is not str:
                raise TypeError("'host' is not a string")

            port = pool['irc']['port']
            if type(port) is not int:
                raise TypeError("'port' is not an integer")

            nick = pool['irc']['nick']
            if type(nick) is not str:
                raise TypeError("'nick' is not a string")

            if "GHI_IRC_PASSWORD" in os.environ:
                password = os.environ["GHI_IRC_PASSWORD"]
            elif 'password' in pool['irc']:
                password = pool['irc']['password']
            else:
                password = None
            if type(password) not in [str, None]:
                raise TypeError("'password' is not a string")

            channels = pool['irc']['channels']
            if type(channels) is not list:
                raise TypeError("'channels' is not a list")

        except (KeyError, TypeError) as e:
            return {
                "statusCode": 500,
                "body": {
                    "success": False,
                    "message": "Missing or invalid parameter in configuration file: %s" % e
                }
            }

        pools.append(
            Pool(
                name=name,
                repos=repos,
                secret=secret,
                host=host,
                port=port,
                nick=nick,
                password=password,
                channels=channels
            )
        )

    # If configuration is valid, return an array of pools
    return {
        "statusCode": 200,
        "pools": pools
    }