import urllib2

from bs4 import BeautifulSoup

from UseProxy import *

class GetMyDrivers(object):
    def __init__(self):
        self.url = 'http://www.mydrivers.com'
        self.content = ''
        self.lists = []

    def split_content(self, proxy_set):
        # self.use_proxy()
        # self.content = proxy_set.get_proxy().open(self.url).read()
        self.content = urllib2.urlopen(self.url).read()
        soup = BeautifulSoup(self.content, "html.parser", from_encoding="gb18030")
        print soup.original_encoding
        found_div = soup.findAll('span', {'class': 'titl'})

        for i in range(len(found_div)):
            self.lists.append(found_div[i].contents[0])
        return self.lists

if __name__ == '__main__':
    g_news = GetMyDrivers()
    proxy_set = UseProxy()
    lists = g_news.split_content(proxy_set)
    for l in lists:
            print str(l).decode('utf-8').encode('utf8')