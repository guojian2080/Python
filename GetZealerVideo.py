from urlparse import urljoin
import urllib2
import re
from UseProxy import *
from bs4 import BeautifulSoup

class GetZealerVideo(object):
    def __init__(self):
        self.url = 'http://www.zealer.com'
        self.content = ''
        self.lists = []

    def split_content(self, proxy_set):
        # self.proxy_set = UseProxy()
        # self.content = proxy_set.getproxy().open(self.url).read().decode('utf-8')
        self.content = urllib2.urlopen(self.url).read().decode('utf-8')
        soup = BeautifulSoup(self.content, "html.parser")
        found_div = soup.findAll('div', {'class': 'subject'})
        found_li = soup.findAll('div', {'id': re.compile("^li_layer")})
        l = len(found_div)
        self.lists = []
        if l == len(found_li):
            for i in range(l):
                b = re.findall('/post/\d+', str(found_li[i]))[0]
                self.lists.append(urljoin(self.url, b))
                self.lists.append(found_div[i].contents[0].encode('utf-8'))
        return self.lists
                    
if __name__ == '__main__':
    g_video = GetZealerVideo()
    proxy_set = UseProxy()
    print '.'.join(g_video.split_content(proxy_set)).decode('utf-8')