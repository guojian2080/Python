import urllib
import urllib2
import urlparse
import time
from time import ctime, sleep
import re
import cookielib
import Queue
import threading
import json

from pyquery import PyQuery as pq

cj = cookielib.CookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
urllib2.install_opener(opener)


home_url = "http://www.hxdai.net"
new_list = []


def get_catalog(detail_html, url):
    detail_doc = pq(detail_html)
    new_dict = {}
    title = detail_doc.find("div[class='content_h3']").text()
    publish_info = detail_doc.find("div[class='content_div']").text()
    content = detail_doc.find("div[class='content_ro2']")
    content_text = content.text()
    content_pic = content.find("p").find("img")

    new_dict["url"] = url
    new_dict["title"] = title.encode("utf8")
    new_dict["publishinfo"] = re.sub(r'\s+', ' ', publish_info.encode("utf8"))
    new_dict["detail"] = content_text.encode("utf8")

    pics = []
    for pic in content_pic:
        pics.append(urlparse.urljoin(home_url, pic.get("src")))
    new_dict["pic"] = pics

    new_list.append(new_dict)


class ThreadUrl(threading.Thread):
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while 1:
            host = self.queue.get()
            response = urllib2.urlopen(host)
            new_text = response.read().decode('utf8')
            response.close()
            list_doc = pq(new_text)
            links = list_doc.find("ul[class='list_li_1']").find("li").find("a")
            for link in links:
                self.out_queue.put(link.get("href"))
            self.queue.task_done()


class DatamineThread(threading.Thread):
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while 1:
            url = urlparse.urljoin(home_url, r"/article/" + self.out_queue.get())
            response = urllib2.urlopen(url)
            detail_html = response.read().decode('utf8')
            url = response.geturl()
            response.close()
            get_catalog(detail_html, url)
            self.out_queue.task_done()


class HxdaiSpider(object):
    """Start the spider
    """
    def __init__(self):
        self.login_url = "http://www.hxdai.net/user/login.html"
        self.headers = {'User-Agent':  'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
           'Referer': '******'}
        self.post_data = {
            "username": "test123456",
            "password": "test123456",
            "actionType": "login",
        }

    def login(self):
        """Get login info"""
        post_data = urllib.urlencode(self.post_data).encode('utf-8')
        request = urllib2.Request(self.login_url, post_data, self.headers)
        response = urllib2.urlopen(request)
        response.close()
        return True

    def get_catalog_list(self, page, filename):
        """Get real catalog url list"""
        queue = Queue.Queue()
        out_queue = Queue.Queue()
        self.login()
        catalog_page = page
        catalog_rep = urllib2.urlopen(catalog_page)
        rcatalog_text = catalog_rep.read().decode('utf8')
        catalog_rep.close()
        try:
            pages = re.findall(r'href=.*?page=(\d+)', rcatalog_text)[-1]
        except IndexError:
            pages = "1"
        print "pages:", pages, "time:", ctime()

        index = int(pages)
        for i in range(index):
            t = ThreadUrl(queue, out_queue)
            t.setDaemon(True)
            t.start()

        for i in range(index):
            tmp_url = "http://www.hxdai.net/article/list.html?catalog=22&page={n}&order=0"
            new_url = tmp_url.format(n=i+1)
            queue.put(new_url)

        for i in range(index):
            dt = DatamineThread(out_queue)
            dt.setDaemon(True)
            dt.start()

        queue.join()
        out_queue.join()
        data_string = json.dumps(new_list, ensure_ascii=False)
        with open(filename, "w") as f:
            json.dump(data_string, f, ensure_ascii=False)
            f.close()

start = time.time()


def main():
    spider = HxdaiSpider()
    # spider.login()

    catalog = "http://www.hxdai.net/article/list.html?catalog=22"
    catalog_txt = "hxdai-article.txt"
    spider.get_catalog_list(catalog, catalog_txt)


print "start at time:", ctime()
main()
print "done at time:", (time.time() - start)
