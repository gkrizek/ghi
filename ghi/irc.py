import json
import socket
import ssl
from time import sleep

class Colors(object):


    def __init__(self):
        self.bold         = "\\002"
        self.reset        = "\\017"
        self.italic       = "\\026"
        self.underline    = "\\037"
        self.white        = "\\0030"
        self.black        = "\\0031"
        self.dark_blue    = "\\0032"
        self.dark_green   = "\\0033"
        self.dark_red     = "\\0034"
        self.brown        = "\\0035"
        self.dark_purple  = "\\0036"
        self.orange       = "\\0037"
        self.yellow       = "\\0038"
        self.light_green  = "\\0039"
        self.dark_teal    = "\\00310"
        self.light_teal   = "\\00311"
        self.light_blue   = "\\00312"
        self.light_purple = "\\00313"
        self.dark_gray    = "\\00314"
        self.light_gray   = "\\00315"


class IRC(object):


    def __init__(self, ssl):
        if ssl is True:
            self.irc = ssl.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                ssl_version=ssl.PROTOCOL_TLSv1_2
            )
        else:
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.settimeout(10)


    def send(self, channel, message):
        self.irc.send(bytes("PRIVMSG {} :{}\n".format(channel, message), "UTF-8"))
 

    def connect(self, host, port, channels, nick, password):
        self.irc.connect((host, port))                                                         
        self.irc.send(bytes("USER {nick} {nick} {nick} {nick}\n".format(nick=nick), "UTF-8"))
        self.irc.send(bytes("NICK {}\n".format(nick), "UTF-8"))
        if password != None:
            self.irc.send(bytes("PRIVMSG NICKSERV :IDENTIFY {}\n".format(password), "UTF-8"))
        for channel in channels:               
            self.irc.send(bytes("JOIN {}\n".format(channel), "UTF-8"))
 

    def disconnect(self, channels):
        for channel in channels:               
            self.irc.send(bytes("PART {}\n".format(channel), "UTF-8"))
        self.irc.send(bytes("QUIT\n", "UTF-8"))
        self.irc.close()

    def get_text(self):
        text=self.irc.recv(2040)
        return text.decode("utf-8")
        

def sendMessages(pool, messages):
    try:
        irc = IRC(pool.ssl)
        irc.connect(pool.host, pool.port, pool.channels, pool.nick, pool.password)

        # Wait until connection is established
        while True:    
            text = irc.get_text()
            if "End of /NAMES list." in text:
                break
            sleep(0.25)

        for channel in pool.channels:
            for message in messages:
                irc.send(channel, message)

        irc.disconnect(pool.channels)

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": "There was a problem sending messages to IRC:\n%s" % e
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "message": "Messages sent successfully."
        }) 
    }