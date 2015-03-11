import web
import re
import base64
from passlib.apache import HtpasswdFile

ht = None

def init(htpasswd_file=".htpasswd"):
    ht = HtpasswdFile(htpasswd_file, new=False)

def check_password(username, password):
    return ht.check_password(username, password)

class restrict1(object):
    """
    Decorator for pages requiring authentication.
    """
    def __init__(self, request):
        object.__init__(self)
        self.__request = request

    def __call__(self, *args, **kwargs):
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ','',auth)
            username,password = base64.decodestring(auth).split(':')
            if check_password(username, password):
                return self.__request(self, *args, **kwargs)
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate','Basic realm="Authentication required"')
            web.ctx.status = '401 Unauthorized'
            return

def restrict(f):
    """
    Decorator for pages requiring authentication.
    """
    def wrapper(*args, **kwargs):
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ','',auth)
            username,password = base64.decodestring(auth).split(':')
            if check_password(username, password):
                return f(*args, **kwargs)
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate','Basic realm="Authentication required"')
            web.ctx.status = '401 Unauthorized'
            return
    return wrapper

ht = HtpasswdFile(".htpasswd", new=False)
