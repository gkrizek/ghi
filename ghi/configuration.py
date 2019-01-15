import json
import logging
import os
import yaml


class Pool(object):


    def __init__(self, name, repos, host, port, ssl, nick, password, channels):
        self.name = name
        self.repos = repos
        self.host = host
        self.port = port
        self.ssl = ssl
        self.nick = nick
        self.password = password
        self.channels = channels


    def containsRepo(self, repo):
        for configRepo in self.repos:                
            if repo == configRepo["name"]:
                return True
        return False


def readFile(path):
    configFile = open(path, "r")
    return configFile.read()


def getConfiguration():

    # Read configuarion file
    # First check if GHI_CONFIG_PATH is set
    # If not, look in os.getcwd, then ~/, then /tmp
    if "GH_CONFIG_PATH" in os.environ:
        configFilePath = os.path.expanduser(os.environ["GH_CONFIG_PATH"])
        
    elif os.path.exists("%s/.ghi.yml" % os.getcwd()):
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
            "body": json.dumps({
                "success": False,
                "message": "Unable to find .ghi.yml file."
            })
        }

    try:
        logging.info("Found configuration file at '%s'" % configFilePath)
        config = yaml.load(readFile(configFilePath))
    except yaml.YAMLError as e:
        logging.error("There was a problem parsing configuation file.")
        logging.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": "Error parsing yaml file:\n%s" % e
            })
        }

    # Validate top level params
    try:
        configVersion = config["version"]
        if type(configVersion) is not int:
            raise TypeError("'version' is not an integer")

        configPools = config["pools"]
        if type(configPools) is not list:
            raise TypeError("'pools' is not a list")

    except (KeyError, TypeError) as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": "Missing or invalid parameter in configuration file: %s" % e
            })
        }

    # for each pool, validate and create a Pool object. append to array
    pools = []
    for pool in configPools:
        # Configuration Validation
        try:
            name = pool["name"]
            if type(name) is not str:
                raise TypeError("'name' is not a string")

            repos = pool["github"]["repos"]
            if type(repos) is not list:
                raise TypeError("'repos' is not a list")
            if len(repos) < 1:
                raise TypeError("'repos' must contain at least 1 item")

            generatedRepos = []
            for repo in repos:
                fullName = repo["name"]
                if type(fullName) is not str:
                    raise TypeError("'name' is not a string")
                
                if fullName.count("/") == 0:
                    raise TypeError("repo name must be the full name. Ex: owner/repo")

                repoOwner = fullName.split("/", maxsplit=1)[0].upper()
                repoName = fullName.split("/", maxsplit=1)[1].upper()

                if "GHI_GITHUB_SECRET_{}_{}".format(repoOwner,repoName) in os.environ:
                    secret = os.environ["GHI_GITHUB_SECRET_{}_{}".format(repoOwner,repoName)]
                else:
                    secret = repo["secret"]
                if type(secret) is not str:
                    raise TypeError("'secret' is not a string")

                if "branches" in repo:
                    branches = repo["branches"]
                    if type(branches) is not list:
                        raise TypeError("'branches' is not a list")
                    if len(branches) < 1:
                        raise TypeError("'branches' must contain at least 1 item")
                else:
                    branches = None

                generatedRepos.append({
                    "name": fullName,
                    "secret": secret,
                    "branches": branches
                })

            host = pool["irc"]["host"]
            if type(host) is not str:
                raise TypeError("'host' is not a string")

            if "ssl" in pool["irc"]:
                ssl = pool["irc"]["ssl"]
                if type(ssl) is not bool:
                    raise TypeError("'ssl' is not a boolean")
            else:
                ssl = True

            if "port" in pool["irc"]:
                port = pool["irc"]["port"]
                if type(port) is not int:
                    raise TypeError("'port' is not an integer")
            elif ssl is True:
                port = 6697
            else:
                port = 6667

            nick = pool["irc"]["nick"]
            if type(nick) is not str:
                raise TypeError("'nick' is not a string")

            if "GHI_IRC_PASSWORD_{}".format(name) in os.environ:
                password = os.environ["GHI_IRC_PASSWORD_{}".format(name)]
            elif "password" in pool["irc"]:
                password = pool["irc"]["password"]
            else:
                password = None
            if password and type(password) is not str:
                raise TypeError("'password' is not a string")

            channels = pool["irc"]["channels"]
            if type(channels) is not list:
                raise TypeError("'channels' is not a list")
            if len(channels) < 1:
                raise TypeError("'channels' must contain at least 1 item")

            generatedChannels = []
            for channel in channels:
                if channel.startswith("#"):
                    generatedChannels.append(channel)
                else:
                    generatedChannels.append("#"+channel)

        except (KeyError, TypeError) as e:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "message": "Missing or invalid parameter in configuration file: %s" % e
                })
            }

        pools.append(
            Pool(
                name=name,
                repos=generatedRepos,
                host=host,
                port=port,
                ssl=ssl,
                nick=nick,
                password=password,
                channels=generatedChannels
            )
        )

    # If configuration is valid, return an array of pools
    return {
        "statusCode": 200,
        "pools": pools
    }