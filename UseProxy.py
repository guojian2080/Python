import urllib2

class UseProxy(object):
    def __init__(self):
        self.user = 'aaaa'
        self.password = 'bbbb'
        self.proxy_server = 'xxx.yyy.zzz:8080'
        self.content = ''

    def get_proxy(self):
        proxy = 'http://{}:{}@{}'.format(self.user, self.password, self.proxy_server)
        proxy_handler = urllib2.ProxyHandler({'http': proxy})
        opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
        return opener