class UnknownProxyError(Exception):
    def __init__(self, proxy_type):
        self.msg = f"The proxy type {proxy_type} is not known\n Try one of socks4, socks5 or http"

class EmailFormatError(Exception):
    
    def __init__(self, msg):
        self.msg = msg

class SMTPRecepientException(Exception): # don't cover

    def __init__(self, code, response):
        self.code = code
        self.response = response