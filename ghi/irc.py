import base64
import json
import logging
import re
import socket
import ssl
from time import sleep


class Colors(object):


    def __init__(self):
        self.bold         = "\002"
        self.reset        = "\017"
        self.italic       = "\026"
        self.underline    = "\037"
        self.white        = "\00300"
        self.black        = "\00301"
        self.dark_blue    = "\00302"
        self.dark_green   = "\00303"
        self.dark_red     = "\00304"
        self.brown        = "\00305"
        self.dark_purple  = "\00306"
        self.orange       = "\00307"
        self.yellow       = "\00308"
        self.light_green  = "\00309"
        self.dark_teal    = "\00310"
        self.light_teal   = "\00311"
        self.light_blue   = "\00312"
        self.light_purple = "\00313"
        self.dark_gray    = "\00314"
        self.light_gray   = "\00315"


class IRC(object):


    def __init__(self, sslConfig):
        if sslConfig is True:
            self.irc = ssl.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                ssl_version=ssl.PROTOCOL_TLSv1_2
            )
        else:
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.settimeout(1)


    def getText(self):
        try:
            text = self.irc.recv()
            return text.decode("UTF-8")
        except socket.timeout:
            return "waiting for messages..."


    def waitAndSee(self, search):
        tries = 0
        while True:
            text = self.getText()
            logging.debug(text)
            ack = re.search(search, text, re.MULTILINE)
            saslFailure = re.search(r'(.*)SASL authentication failed(.*)', text, re.MULTILINE)
            if ack:
                return
            elif saslFailure:
                raise ConnectionError("Unable to connect to IRC: SASL Authentication Failure") 
            elif tries > 20:
                # If tried more than 20 times with no result, raise error
                raise ConnectionError("Unable to connect to IRC: %s" % text)
            sleep(0.25)
            tries += 1


    def authenticate(self, nick, password):
        self.irc.send(bytes("CAP REQ :sasl\r\n", "UTF-8"))
        self.waitAndSee(r'(.*)CAP(.*)ACK(.*)')
        self.irc.send(bytes("AUTHENTICATE PLAIN\r\n", "UTF-8"))
        self.waitAndSee(r'(.*)AUTHENTICATE \+(.*)')
        auth = (
            "{nick}\0{nick}\0{password}"
        ).format(
            nick=nick,
            password=password
        )
        auth = base64.encodestring(auth.encode("UTF-8"))
        auth = auth.decode("UTF-8").rstrip("\n")
        self.irc.send(bytes("AUTHENTICATE "+auth+"\r\n", "UTF-8"))
        self.waitAndSee(r'(.*)903(.*):SASL authentication successful(.*)')
        self.irc.send(bytes("CAP END\r\n", "UTF-8"))


    def sendMessage(self, channel, message):
        self.irc.send(bytes("PRIVMSG {} :{}\r\n".format(channel, message), "UTF-8"))


    def sendPong(self, text):
        self.irc.send(bytes(text.replace('PING', 'PONG'), "UTF-8"))


    def connect(self, host, port, channels, nick, password):
        logging.info("Connecting to {}:{} with nick {} and channels: {}".format(host, port, nick, ','.join(channels)))
        self.irc.connect((host, port))  
        if password != None:
            self.authenticate(nick, password)                                                  
        self.irc.send(bytes("USER {nick} {nick} {nick} {nick}\r\n".format(nick=nick), "UTF-8"))
        self.irc.send(bytes("NICK {}\r\n".format(nick), "UTF-8"))
        for channel in channels:          
            self.irc.send(bytes("JOIN {}\r\n".format(channel), "UTF-8"))
 

    def disconnect(self, channels):
        # Don't disconnect too soon to ensure messages are sent
        sleep(1)
        for channel in channels:               
            self.irc.send(bytes("PART {}\r\n".format(channel), "UTF-8"))
        self.irc.send(bytes("QUIT\r\n", "UTF-8"))
        # Get rest of logs for debug
        tries = 0
        while True:
            text = self.getText()
            logging.debug(text)
            ack = re.search(r'(.*)QUIT :Client Quit(.*)', text, re.MULTILINE)
            if ack:
                break
            elif tries > 15:
                logging.info("Timeout waiting to quit IRC. Forcefully disconnecting now.")
                break
            sleep(0.25)
            tries += 1

        self.irc.close()
        logging.info("Disconnected from IRC")
        

def sendMessages(pool, messages):
    try:
        irc = IRC(pool.ssl)
        irc.connect(pool.host, pool.port, pool.channels, pool.nick, pool.password)
        
        # Wait until connection is established
        connectionTries = 0
        while True:
            text = irc.getText()
            for line in text.split('\r'):
                logging.debug(line.rstrip())
            if re.search(r'(.*)00[1-4] '+pool.nick+'(.*)', text, re.MULTILINE):
                break
            elif re.search(r'(.*)PING(.*)', text, re.MULTILINE):
                irc.sendPong(text)
            elif re.search(r'(.*)433(.*)Nickname is already in use(.*)', text, re.MULTILINE):
                raise ConnectionError("Nickname is already in use")
            elif re.search(r'(.*)ERROR :(.*)', text, re.MULTILINE):
                raise ConnectionError(text)
            elif connectionTries > 20:
                # If tried 20 times and no match, raise error
                raise ConnectionError("Timeout trying to connect to IRC.")
            sleep(0.25)
            connectionTries += 1

        logging.info("Connection Successful")

        for channel in pool.channels:
            for message in messages:
                irc.sendMessage(channel, message)

        # Wait until messages were successfully sent
        sendTries = 0
        while True:
            text = irc.getText()
            for line in text.split('\r'):
                logging.debug(line.rstrip())
            if re.search(r'(.*)End of /NAMES list(.*)', text, re.MULTILINE):
                break
            elif sendTries > 120:
                # If tried 120 times and no match, raise error
                raise ConnectionError("Timeout sending messages to IRC.")
            sleep(0.25)
            sendTries += 1

        irc.disconnect(pool.channels)

        resultMessage = "Successfully sent {} messages.".format(len(messages))
        logging.info(resultMessage)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": resultMessage
            }) 
        }

    except Exception as e:
        errorMessage = "There was a problem sending messages to IRC"
        logging.error(errorMessage)
        logging.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": errorMessage
            })
        }
