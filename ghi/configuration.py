import json
import logging
import os
import yaml

SUPPORTED_OUTLETS = ["irc", "mastodon", "matrix"]
MATRIX_DEVICE_ID = "Ghi-Matrix-Bot"

class Pool(object):


    def __init__(self, name, outlets, repos, shorten, ircHost, ircPort, ircSsl, ircNick, ircPassword, ircChannels,\
                 mastInstance, mastUser, mastPassword, mastSecPath, mastAppName, mastMergeFilter,\
                 matrixUser, matrixPassword, matrixServer, matrixRooms, matrixSecPath, matrixDevId):
        self.name = name
        self.outlets = outlets
        self.repos = repos
        self.shorten = shorten
        self.ircHost = ircHost
        self.ircPort = ircPort
        self.ircSsl = ircSsl
        self.ircNick = ircNick
        self.ircPassword = ircPassword
        self.ircChannels = ircChannels
        self.mastInstance = mastInstance
        self.mastUser = mastUser
        self.mastPassword = mastPassword
        self.mastSecPath = mastSecPath
        self.mastAppName = mastAppName
        self.mastMergeFilter = mastMergeFilter
        self.matrixUser = matrixUser
        self.matrixPassword = matrixPassword
        self.matrixServer = matrixServer
        self.matrixRooms = matrixRooms
        self.matrixSecPath = matrixSecPath
        self.matrixDevId = matrixDevId


    def containsRepo(self, repo):
        for configRepo in self.repos:
            if repo == configRepo["name"]:
                return True
        return False


def readFile(path):
    configFile = open(path, "r")
    return configFile.read()


class GlobalConfig(object):


    def __init__(self, ircHost, ircPort, ircSsl, ircNick, ircPassword, mastInstance, mastUser,\
                 mastPassword, mastSecPath, mastAppName, mastMergeFilter, shorten, verify, outlets,\
                 matrixUser, matrixPassword, matrixServer, matrixSecPath, matrixDevId):
        self.ircHost = ircHost
        self.ircPort = ircPort
        self.ircSsl = ircSsl
        self.ircNick = ircNick
        self.ircPassword = ircPassword
        self.mastInstance = mastInstance
        self.mastUser = mastUser
        self.mastPassword = mastPassword
        self.mastSecPath = mastSecPath
        self.mastAppName = mastAppName
        self.mastMergeFilter = mastMergeFilter
        self.shorten = shorten
        self.verify = verify
        self.outlets = outlets
        self.matrixUser = matrixUser
        self.matrixPassword = matrixPassword
        self.matrixServer = matrixServer
        self.matrixSecPath = matrixSecPath
        self.matrixDevId = matrixDevId


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
                raise TypeError("'debug' is not a boolean")
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
                globalIrcHost = globalConfig["irc"]["host"]
                if type(globalIrcHost) is not str:
                    raise TypeError("'host' is not a string")
            else:
                globalIrcHost = None
            
            if "port" in globalConfig["irc"]:
                globalIrcPort = globalConfig["irc"]["port"]
                if type(globalIrcPort) is not int:
                    raise TypeError("'port' is not a integer")
            else:
                globalIrcPort = None

            if "ssl" in globalConfig["irc"]:
                globalIrcSsl = globalConfig["irc"]["ssl"]
                if type(globalIrcSsl) is not bool:
                    raise TypeError("'ssl' is not a boolean")
            else:
                globalIrcSsl = None

            if "nick" in globalConfig["irc"]:
                globalIrcNick = globalConfig["irc"]["nick"]
                if type(globalIrcNick) is not str:
                    raise TypeError("'nick' is not a string")
            else:
                globalIrcNick = None

            if "password" in globalConfig["irc"]:
                globalIrcPassword = globalConfig["irc"]["password"]
                if type(globalIrcPassword) is not str:
                    raise TypeError("'password' is not a string")
            else:
                globalIrcPassword = None
        else:
            globalIrcHost = None
            globalIrcPort = None
            globalIrcSsl = None
            globalIrcNick = None
            globalIrcPassword = None

        if "mastodon" in globalConfig:
            if "instance" in globalConfig["mastodon"]:
                globalMastInstance = globalConfig["mastodon"]["instance"]
                if type(globalMastInstance) is not str:
                    raise TypeError("'instance' is not a string")
            else:
                globalMastInstance = None

            if "user" in globalConfig["mastodon"]:
                globalMastUser = globalConfig["mastodon"]["user"]
                if type(globalMastUser) is not str:
                    raise TypeError("'user' is not a string")
            else:
                globalMastUser = None

            if "password" in globalConfig["mastodon"]:
                globalMastPassword = globalConfig["mastodon"]["password"]
                if type(globalMastPassword) is not str:
                    raise TypeError("'password' is not a string")
            else:
                globalMastPassword = None

            if "secretspath" in globalConfig["mastodon"]:
                globalMastSecPath = globalConfig["mastodon"]["secretspath"]
                if type(globalMastSecPath) is not str:
                    raise TypeError("'secretspath' is not a string")
            else:
                globalMastSecPath = None

            if "appname" in globalConfig["mastodon"]:
                globalMastAppName = globalConfig["mastodon"]["appname"]
                if type(globalMastAppName) is not str:
                    raise TypeError("'appname' is not a string")
            else:
                globalMastAppName = None

            if "merges_only" in globalConfig["mastodon"]:
                globalMastMergeFilter = globalConfig["mastodon"]["merges_only"]
                if type(globalMastMergeFilter) is not bool:
                    raise TypeError("'merges_only' is not a boolean")
            else:
                globalMastMergeFilter = None
        else:
            globalMastInstance = None
            globalMastUser = None
            globalMastPassword = None
            globalMastSecPath = None
            globalMastAppName = None
            globalMastMergeFilter = None

        if "matrix" in globalConfig:
            if "user" in globalConfig["matrix"]:
                globalMatrixUser = globalConfig["matrix"]["user"]
                if type(globalMatrixUser) is not str:
                    raise TypeError("'user' is not a string")
            else:
                globalMatrixUser = None

            if "password" in globalConfig["matrix"]:
                globalMatrixPassword = globalConfig["matrix"]["password"]
                if type(globalMatrixPassword) is not str:
                    raise TypeError("'password' is not a string")
            else:
                globalMatrixPassword = None

            if "homeserver" in globalConfig["matrix"]:
                globalMatrixServer = globalConfig["matrix"]["homeserver"]
                if type(globalMatrixServer) is not str:
                    raise TypeError("'homeserver' is not a string")
            else:
                globalMatrixServer = None

            if "secretspath" in globalConfig["matrix"]:
                globalMatrixSecPath = globalConfig["matrix"]["secretspath"]
                if type(globalMatrixSecPath) is not str:
                    raise TypeError("'secretspath' is not a string")
            else:
                globalMatrixSecPath = None

            if "device_id" in globalConfig["matrix"]:
                globalMatrixDevId = globalConfig["matrix"]["device_id"]
                if type(globalMatrixDevId) is not str:
                    raise TypeError("'device_id' is not a string")
            else:
                globalMatrixDevId = MATRIX_DEVICE_ID
        else:
            globalMatrixUser = None
            globalMatrixPassword = None
            globalMatrixServer = None
            globalMatrixSecPath = None
            globalMatrixDevId = None

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


        if "outlets" in globalConfig:
            outlets = globalConfig["outlets"]
            if type(outlets) is not list:
                raise TypeError("'outlets' is not a list")
            if len(outlets) <1:
                raise TypeError("'outlets' must contain at least 1 item")
        else:
            outlets = None

        globalGeneratedOutlets = []
        if outlets != None:
            for outlet in outlets:
                if outlet in SUPPORTED_OUTLETS:
                    globalGeneratedOutlets.append(outlet)
                else:
                    raise ValueError("'{entry}' is not supported.".format(entry=outlet))
        else:
            globalGeneratedOutlets = None

        globalSettings = GlobalConfig(
            ircHost         = globalIrcHost,
            ircPort         = globalIrcPort,
            ircSsl          = globalIrcSsl,
            ircNick         = globalIrcNick,
            ircPassword     = globalIrcPassword,
            mastInstance    = globalMastInstance,
            mastUser        = globalMastUser,
            mastPassword    = globalMastPassword,
            mastSecPath     = globalMastSecPath,
            mastAppName     = globalMastAppName,
            mastMergeFilter = globalMastMergeFilter,
            matrixUser      = globalMatrixUser,
            matrixPassword  = globalMatrixPassword,
            matrixServer    = globalMatrixServer,
            matrixSecPath   = globalMatrixSecPath,
            matrixDevId     = globalMatrixDevId,
            shorten         = globalShorten,
            verify          = globalVerify,
            outlets         = globalGeneratedOutlets
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


            if "outlets" in pool:
                outlets = pool["outlets"]
                if type(outlets) is not list:
                    raise TypeError("'outlets' is not a list")
                if len(outlets) <1:
                    raise TypeError("'outlets' must contain at least 1 item")
            else:
                outlets = None

            generatedOutlets = []
            if outlets != None:
                for outlet in outlets:
                    if outlet in SUPPORTED_OUTLETS:
                        generatedOutlets.append(outlet)
                    else:
                        raise ValueError("'{entry}' is not supported.".format(entry=outlet))
            elif globalSettings.outlets:
                generatedOutlets = globalSettings.outlets
            else:
                generatedOutlets = ["irc"]


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


            if "irc" in generatedOutlets:
                if "host" in pool["irc"]:
                    ircHost = pool["irc"]["host"]
                elif globalSettings.ircHost:
                    ircHost = globalSettings.ircHost
                else:
                    raise KeyError("host")
                if type(ircHost) is not str:
                    raise TypeError("'host' is not a string")


                if "ssl" in pool["irc"]:
                    ircSsl = pool["irc"]["ssl"]
                elif globalSettings.ircSsl:
                    ircSsl = globalSettings.ircSsl
                else:
                    ircSsl = True
                if type(ircSsl) is not bool:
                    raise TypeError("'ssl' is not a boolean")


                if "port" in pool["irc"]:
                    ircPort = pool["irc"]["port"]
                elif globalSettings.ircPort:
                    ircPort = globalSettings.ircPort
                elif ircSsl is True:
                    ircPort = 6697
                else:
                    ircPort = 6667
                if type(ircPort) is not int:
                    raise TypeError("'port' is not an integer")


                if "nick" in pool["irc"]:
                    ircNick = pool["irc"]["nick"]
                elif globalSettings.ircNick:
                    ircNick = globalSettings.ircNick
                else:
                    raise KeyError("nick")
                if type(ircNick) is not str:
                    raise TypeError("'nick' is not a string")

                envName = name.upper()
                envName = ''.join(l for l in envName if l.isalnum())
                if "GHI_IRC_PASSWORD_{}".format(envName) in os.environ:
                    ircPassword = os.environ["GHI_IRC_PASSWORD_{}".format(envName)]
                elif "password" in pool["irc"]:
                    ircPassword = pool["irc"]["password"]
                elif globalSettings.ircPassword:
                    ircPassword = globalSettings.ircPassword
                else:
                    ircPassword = None
                if ircPassword and type(ircPassword) is not str:
                    raise TypeError("'password' is not a string")


                ircChannels = pool["irc"]["channels"]
                if type(ircChannels) is not list:
                    raise TypeError("'channels' is not a list")
                if len(ircChannels) < 1:
                    raise TypeError("'channels' must contain at least 1 item")

                generatedIrcChannels = []
                for channel in ircChannels:
                    if channel.startswith("#"):
                        generatedIrcChannels.append(channel)
                    else:
                        generatedIrcChannels.append("#"+channel)

            if "mastodon" in generatedOutlets and "mastodon" in pool:
                if "instance" in pool["mastodon"]:
                    mastInstance = pool["mastodon"]["instance"]
                elif globalSettings.mastInstance:
                    mastInstance = globalSettings.mastInstance
                else:
                    raise KeyError("instance")
                if type(mastInstance) is not str:
                    raise TypeError("'instance' is not a string")


                if "user" in pool["mastodon"]:
                    mastUser = pool["mastodon"]["user"]
                elif globalSettings.mastUser:
                    mastUser = globalSettings.mastUser
                else:
                    raise KeyError("user")
                if type(mastUser) is not str:
                    raise TypeError("'user' is not a string")


                if "password" in pool["mastodon"]:
                    mastPassword = pool["mastodon"]["password"]
                elif globalSettings.mastPassword:
                    mastPassword = globalSettings.mastPassword
                else:
                    raise KeyError("password")
                if type(mastPassword) is not str:
                    raise TypeError("'password' is not a string")


                if "secretspath" in pool["mastodon"]:
                    mastSecPath = pool["mastodon"]["secretspath"]
                elif globalSettings.mastSecPath:
                    mastSecPath = globalSettings.mastSecPath
                else:
                    raise KeyError("secretspath")
                if type(mastSecPath) is not str:
                    raise TypeError("'secretspath' is not a string")


                if "appname" in pool["mastodon"]:
                    mastAppName = pool["mastodon"]["appname"]
                elif globalSettings.mastAppName:
                    mastAppName = globalSettings.mastAppName
                else:
                    raise KeyError("appname")
                if type(mastAppName) is not str:
                    raise TypeError("'appname' is not a string")


                if "merges_only" in pool["mastodon"]:
                    mastMergeFilter = pool["mastodon"]["merges_only"]
                elif globalSettings.mastMergeFilter:
                    mastMergeFilter = globalSettings.mastMergeFilter
                else:
                    mastMergeFilter = True
                if type(mastMergeFilter) is not bool:
                    raise TypeError("'merges_only' is not a boolean")

            elif "mastodon" in generatedOutlets and "mastodon" in globalConfig:
                if globalSettings.mastInstance:
                    mastInstance = globalSettings.mastInstance
                else:
                    raise KeyError("instance")

                if globalSettings.mastUser:
                    mastUser = globalSettings.mastUser
                else:
                    raise KeyError("user")

                if globalSettings.mastPassword:
                    mastPassword = globalSettings.mastPassword
                else:
                    raise KeyError("password")

                if globalSettings.mastSecPath:
                    mastSecPath = globalSettings.mastSecPath
                else:
                    raise KeyError("secretspath")

                if globalSettings.mastAppName:
                    mastAppName = globalSettings.mastAppName
                else:
                    raise KeyError("appname")

                if globalSettings.mastMergeFilter:
                    mastMergeFilter = globalSettings.mastMergeFilter
                else:
                    mastMergeFilter = True

            if "matrix" in generatedOutlets and "matrix" in pool:
                if "user" in pool["matrix"]:
                    matrixUser = pool["matrix"]["user"]
                elif globalSettings.matrixUser:
                    matrixUser = globalSettings.matrixUser
                else:
                    raise KeyError("user")
                if type(matrixUser) is not str:
                    raise TypeError("'user' is not a string")

                if "password" in pool["matrix"]:
                    matrixPassword = pool["matrix"]["password"]
                elif globalSettings.matrixPassword:
                    matrixPassword = globalSettings.matrixPassword
                else:
                    raise KeyError("password")
                if type(matrixPassword) is not str:
                    raise TypeError("'password' is not a string")

                if "homeserver" in pool["matrix"]:
                    matrixServer = pool["matrix"]["homeserver"]
                elif globalSettings.matrixServer:
                    matrixServer = globalSettings.matrixServer
                else:
                    raise KeyError("homeserver")
                if type(matrixServer) is not str:
                    raise TypeError("'homeserver' is not a string")

                if "secretspath" in pool["matrix"]:
                    matrixSecPath = pool["matrix"]["secretspath"]
                elif globalSettings.matrixSecPath:
                    matrixSecPath = globalSettings.matrixSecPath
                else:
                    raise KeyError("secretspath")
                if type(matrixSecPath) is not str:
                    raise TypeError("'secretspath' is not a string")

                if "device_id" in pool["matrix"]:
                    matrixDevId = pool["matrix"]["device_id"]
                elif globalSettings.matrixDevId:
                    matrixDevId = globalSettings.matrixDevId
                else:
                    matrixDevId = MATRIX_DEVICE_ID
                if type(matrixDevId) is not str:
                    raise TypeError("'device_id' is not a string")

                if "rooms" in pool["matrix"]:
                    matrixRooms = pool["matrix"]["rooms"]
                else:
                    raise KeyError("rooms")
                if type(matrixRooms) is not list:
                    raise TypeError("'rooms' is not a list")
                if len(matrixRooms) < 1:
                    raise TypeError("'rooms' must contain at least 1 item")

                generatedMatrixRooms = list()
                for room in matrixRooms:
                    generatedMatrixRooms.append(room)#"+room)

            elif "matrix" in generatedOutlets and "matrix" in globalConfig:
                if globalSettings.matrixUser:
                    matrixUser = globalSettings.matrixUser
                else:
                    raise KeyError("user")

                if globalSettings.matrixPassword:
                    matrixPassword = globalSettings.matrixPassword
                else:
                    raise KeyError("password")

                if globalSettings.matrixServer:
                    matrixServer = globalSettings.matrixServer
                else:
                    raise KeyError("homeserver")

                if globalSettings.matrixSecPath:
                    matrixSecPath = globalSettings.matrixSecPath
                else:
                    raise KeyError("secretspath")

                if globalSettings.matrixDevId:
                    matrixDevId = globalSettings.matrixDevId
                else:
                    matrixDevId = MATRIX_DEVICE_ID

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

        if "irc" not in generatedOutlets:
            ircHost = None
            ircPort = None
            ircSsl = None
            ircNick = None
            ircPassword = None
            generatedIrcChannels = None

        if "mastodon" not in generatedOutlets:
            mastInstance = None
            mastUser = None
            mastPassword = None
            mastSecPath = None
            mastAppName = None
            mastMergeFilter = None

        if "matrix" not in generatedOutlets:
            matrixUser = None
            matrixPassword = None
            matrixServer = None
            generatedMatrixRooms = None
            matrixSecPath = None
            matrixDevId = None

        pools.append(
            Pool(
                name=name,
                outlets=generatedOutlets,
                repos=generatedRepos,
                shorten=shorten,
                ircHost=ircHost,
                ircPort=ircPort,
                ircSsl=ircSsl,
                ircNick=ircNick,
                ircPassword=ircPassword,
                ircChannels=generatedIrcChannels,
                mastInstance=mastInstance,
                mastUser=mastUser,
                mastPassword=mastPassword,
                mastSecPath=mastSecPath,
                mastAppName=mastAppName,
                mastMergeFilter=mastMergeFilter,
                matrixUser=matrixUser,
                matrixPassword=matrixPassword,
                matrixServer=matrixServer,
                matrixRooms=generatedMatrixRooms,
                matrixSecPath=matrixSecPath,
                matrixDevId=matrixDevId
            )
        )

    # If configuration is valid, return an array of pools
    return {
        "statusCode": 200,
        "debug": debug,
        "pools": pools
    }
