import logging
import os
import yaml


class Pool(object):

    def __init__(self, name, repos, secret, host, port, username, nick, realname, password, channels):
        self.name = name
        self.repos = repos
        self.secret = secret
        self.host = host
        self.port = port
        self.username = username
        self.nick = nick
        self.realname = realname
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
        configFilePath = "%s/.ghi.yml" % os.getcwd()

    elif os.path.exists(os.path.expanduser("~/.ghi.yaml")):
        configFilePath = "%s/.ghi.yaml" % os.getcwd()

    elif os.path.exists("/tmp/.ghi.yml"):
        configFilePath = "%s/.ghi.yml" % os.getcwd()

    elif os.path.exists("/tmp/.ghi.yaml"):
        configFilePath = "%s/.ghi.yaml" % os.getcwd()

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



    # return array and a status. Send non 200 if problems
    


    return