

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


def sendMessages(pool, messages):

    return