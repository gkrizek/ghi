import json
import logging
import os
import yaml


class Pool(object):


    def __init__(self, name, repos, shorten, host, port, ssl, nick, password, channels):
        self.name = name
        self.repos = repos
        self.shorten = shorten
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


class GlobalConfig(object):


    def __init__(self, host, port, ssl, nick, password, shorten, verify):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.nick = nick
        self.password = password
        self.shorten = shorten
        self.verify = verify


def getConfiguration():

    # Read configuarion file
    # First check if GHI_CONFIG_PATH is set
    # If not, look in os.getcwd, then ~/, then /tmp
    if "GHI_CONFIG_PATH" in os.environ:
        configFilePath = os.path.expanduser(os.environ["GHI_CONFIG_PATH"])
        
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
        logging.error("There was a problem parsing configuration file.")
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
        elif configVersion not in [1]:
            raise ValueError("Invalid version")

        configPools = config["pools"]
        if type(configPools) is not list:
            raise TypeError("'pools' is not a list")

        if "global" in config:
            globalConfig = config["global"]
            if type(globalConfig) is not dict:
                raise TypeError("'global' is not a dict")
        else:
            globalConfig = {}

        if "debug" in config:
            debug = config["debug"]
            if type(debug) is not bool:
                raise TypeError("'pools' is not a boolean")
        else:
            debug = False

    except (KeyError, TypeError) as e:
        errorMessage = "Missing or invalid parameter in configuration file: %s" % e
        logging.error(errorMessage)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": errorMessage
            })
        }

    # GLOBAL
    # validate and set global parameters
    try:
        if "irc" in globalConfig:
            if "host" in globalConfig["irc"]:
                globalHost = globalConfig["irc"]["host"]
                if type(globalHost) is not str:
                    raise TypeError("'host' is not a string")
            else:
                globalHost = None
            
            if "port" in globalConfig["irc"]:
                globalPort = globalConfig["irc"]["port"]
                if type(globalPort) is not int:
                    raise TypeError("'port' is not a integer")
            else:
                globalPort = None

            if "ssl" in globalConfig["irc"]:
                globalSsl = globalConfig["irc"]["ssl"]
                if type(globalSsl) is not bool:
                    raise TypeError("'ssl' is not a boolean")
            else:
                globalSsl = None

            if "nick" in globalConfig["irc"]:
                globalNick = globalConfig["irc"]["nick"]
                if type(globalNick) is not str:
                    raise TypeError("'nick' is not a string")
            else:
                globalNick = None

            if "password" in globalConfig["irc"]:
                globalPassword = globalConfig["irc"]["password"]
                if type(globalPassword) is not str:
                    raise TypeError("'password' is not a string")
            else:
                globalPassword = None
        else:
            globalHost = None
            globalPort = None
            globalSsl = None
            globalNick = None
            globalPassword = None

        if "github" in globalConfig:
            if "shorten_url" in globalConfig["github"]:
                globalShorten = globalConfig["github"]["shorten_url"]
                if type(globalShorten) is not bool:
                    raise TypeError("'shorten_url' is not a boolean")
            else:
                globalShorten = None
            
            if "verify" in globalConfig["github"]:
                globalVerify = globalConfig["github"]["verify"]
                if type(globalVerify) is not bool:
                    raise TypeError("'verify' is not a boolean")
            else:
                globalVerify = None
        else:
            globalShorten = None
            globalVerify = None

        globalSettings = GlobalConfig(
            host     = globalHost,
            port     = globalPort,
            ssl      = globalSsl,
            nick     = globalNick,
            password = globalPassword,
            shorten  = globalShorten,
            verify   = globalVerify
        )
    except (KeyError, TypeError) as e:
        errorMessage = "Missing or invalid parameter in configuration file: %s" % e
        logging.error(errorMessage)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": errorMessage
            })
        }

    # POOLS
    # for each pool, validate and create a Pool object, append to array
    globalRepos = []
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


            if "shorten_url" in pool["github"]:
                shorten = pool["github"]["shorten_url"]
            elif globalSettings.shorten:
                shorten = globalSettings.shorten
            else:
                shorten = False
            if type(shorten) is not bool:
                raise TypeError("'shorten_url' is not a boolean")
                

            generatedRepos = []
            for repo in repos:
                fullName = repo["name"]
                if type(fullName) is not str:
                    raise TypeError("'name' is not a string")
                
                if fullName.count("/") == 0:
                    raise TypeError("repo name must be the full name. Ex: owner/repo")

                if fullName in globalRepos:
                    raise ValueError("Duplicate repo in config: %s" % fullName)

                if "verify" in repo:
                    verifyPayload = repo["verify"]
                elif globalSettings.verify is not None:
                    verifyPayload = globalSettings.verify
                else:
                    verifyPayload = True
                if type(verifyPayload) is not bool:
                    raise TypeError("'verify' is not a boolean")
                repo["verify"] = verifyPayload

                if repo["verify"] or globalSettings.verify:
                    repoOwner = fullName.split("/", maxsplit=1)[0].upper()
                    repoName = fullName.split("/", maxsplit=1)[1].upper()
                    # Remove special characters
                    repoName = ''.join(l for l in repoName if l.isalnum())

                    if "GHI_GITHUB_SECRET_{}_{}".format(repoOwner,repoName) in os.environ:
                        secret = os.environ["GHI_GITHUB_SECRET_{}_{}".format(repoOwner,repoName)]
                    else:
                        secret = repo["secret"]
                    if type(secret) is not str:
                        raise TypeError("'secret' is not a string")
                else:
                    secret = None

                if "branches" in repo:
                    branches = repo["branches"]
                    if type(branches) is not list:
                        raise TypeError("'branches' is not a list")
                    if len(branches) < 1:
                        raise TypeError("'branches' must contain at least 1 item")
                    branches = [str(branch) for branch in branches]
                else:
                    branches = None
                

                globalRepos.append(fullName)
                generatedRepos.append({
                    "name": fullName,
                    "secret": secret,
                    "branches": branches,
                    "verify": verifyPayload
                })


            if "host" in pool["irc"]:
                host = pool["irc"]["host"]
            elif globalSettings.host:
                host = globalSettings.host
            else:
                raise KeyError("host")
            if type(host) is not str:
                raise TypeError("'host' is not a string")


            if "ssl" in pool["irc"]:
                ssl = pool["irc"]["ssl"]
            elif globalSettings.ssl:
                ssl = globalSettings.ssl
            else:
                ssl = True
            if type(ssl) is not bool:
                raise TypeError("'ssl' is not a boolean")


            if "port" in pool["irc"]:
                port = pool["irc"]["port"]
            elif globalSettings.port:
                port = globalSettings.port
            elif ssl is True:
                port = 6697
            else:
                port = 6667
            if type(port) is not int:
                raise TypeError("'port' is not an integer")


            if "nick" in pool["irc"]:
                nick = pool["irc"]["nick"]
            elif globalSettings.nick:
                nick = globalSettings.nick
            else:
                raise KeyError("nick")
            if type(nick) is not str:
                raise TypeError("'nick' is not a string")

            envName = name.upper()
            envName = ''.join(l for l in envName if l.isalnum())
            if "GHI_IRC_PASSWORD_{}".format(envName) in os.environ:
                password = os.environ["GHI_IRC_PASSWORD_{}".format(envName)]
            elif "password" in pool["irc"]:
                password = pool["irc"]["password"]
            elif globalSettings.password:
                password = globalSettings.password
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
            errorMessage = "Missing or invalid parameter in configuration file: %s" % e
            logging.error(errorMessage)
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "message": errorMessage
                })
            }
        pools.append(
            Pool(
                name=name,
                repos=generatedRepos,
                shorten=shorten,
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
        "debug": debug,
        "pools": pools
    }
