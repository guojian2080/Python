import urllib
import urllib2
import urlparse
import time
from time import ctime
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


def get_bid(detail_html, url):
    keys = ['money', 'profit', 'repaymentMode', 'rewards', 'timeLimit', 'bidNumber', 'completeness', 'bidLimit']
    member_key = ["sex", "marriage", "local", "birth", "degree", "job"]
    financial_key = ["beenpayed", "topay", "aheadpay", "in30overdue", "out30overdue", "overdue",
                     "borrow", "loan", "recharge", "withdraw", "needpay", "getpay"]
    new_dict = {}
    detail_doc = pq(detail_html)
    new_dict["bid-url"] = url

    title = detail_doc.find("div[id='modal_dialog']")
    new_dict["title"] = title.attr("title").encode('utf8')

    user_main = detail_doc.find("div[class='box-info-user second-border-user']")
    p = user_main.find("p")
    new_dict["username"] = pq(p[0]).text().encode("utf8")
    new_dict["userscore"] = pq(p[1]).text().encode("utf8")

    user_photo = user_main.find("img")
    new_dict[user_photo.attr("class")] = urlparse.urljoin(home_url, user_photo.attr("src"))

    user_info = user_main.find("div[class='info_a']").find("div")
    for info in user_info:
        info_doc = pq(info)
        new_dict[info_doc.attr("class")] = info_doc.attr("title").encode('utf8')

    member_info = detail_doc.find("div[class='hyxx second-right-box']").find("ul[class='clearfix']").find("li")
    for i in range(len(member_key)):
        new_dict[member_key[i]] = pq(member_info[i]).text().encode('utf8')

    financial_info = detail_doc.find("div[class='zjzk second-right-box']").find("ul[class='clearfix']").find("li")
    for i in range(len(financial_key)):
        new_dict[financial_key[i]] = pq(financial_info[i]).text().encode('utf8')

    ul = detail_doc("div[class='box-info-detail']").find("ul[class='clearfix']").find("li")
    length = len(ul)
    for i in range(length):
        new_dict[keys[i]] = pq(ul[i]).text().encode('utf8')

    jkxq = detail_doc.find("div[id='jkxq']")
    new_dict["jkxqInfo"] = jkxq.find("p").text().encode('utf8')
    new_dict["jkxqImg"] = urlparse.urljoin(home_url, jkxq.find("img").attr("src"))

    bid_info = detail_doc.find("div[id='zlsh']").find("li[class='clearfix']")
    length1 = len(bid_info)

    bids = []
    for i in range(1, length1):
        bids.append(pq(bid_info[i]).find("dd").text().encode("utf8"))

    new_dict["bidinfo"] = bids

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
            links = list_doc("a[class='titletxt']")
            for link in links:
                self.out_queue.put(link.get("href"))
            self.queue.task_done()


class DatamineThread(threading.Thread):
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while 1:
            url = urlparse.urljoin(home_url, self.out_queue.get())
            response = urllib2.urlopen(url)
            detail_html = response.read().decode('utf8')
            url = response.geturl()
            print url
            response.close()
            get_bid(detail_html, url)
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

    def get_bid_list(self, page, status, filename):
        """Get real bid url list"""
        queue = Queue.Queue()
        out_queue = Queue.Queue()
        global new_list
        self.login()
        repay_page = page
        repay_rep = urllib2.urlopen(repay_page)
        print "get first list at time", ctime()
        repay_text = repay_rep.read().decode('utf8')
        repay_rep.close()
        try:
            pages = re.findall(r'href=.*?page=(\d+)', repay_text)[-1]
        except IndexError:
            pages = "1"
        print "pages:", pages, "time:", ctime()

        index = int(pages)
        for i in range(index):
            t = ThreadUrl(queue, out_queue)
            t.setDaemon(True)
            t.start()

        for i in range(index):
            tmp_url = "http://www.hxdai.net/invest/index.html?search=select&status={s}&page={n}&order=8"
            new_url = tmp_url.format(s=status, n=i+1)
            queue.put(new_url)

        for i in range(index):
            dt = DatamineThread(out_queue)
            dt.setDaemon(True)
            dt.start()

        queue.join()
        out_queue.join()
        print new_list
        '''
        data_string = json.dumps(new_list, ensure_ascii=False)
        with open(filename, "w") as f:
            json.dump(data_string, f, ensure_ascii=False)
            f.close()
        '''

start = time.time()


def main():
    spider = HxdaiSpider()
    # spider.login()

    loan_page = "http://www.hxdai.net/invest/index.html?status=1"
    loan_txt = "hxdai-loaninvest.txt"
    spider.get_bid_list(loan_page, "1", loan_txt)

    repay_page = "http://www.hxdai.net/invest/index.html?status=10"
    repay_txt = "hxdai-repayinvest.txt"
    print "repaypage"
    new_list = []
    spider.get_bid_list(repay_page, "10", repay_txt)

    done_page = "http://www.hxdai.net/invest/index.html?status=12"
    done_txt = "hxdai-doneinvest.txt"
    print "donepage"
    new_list = []
    # spider.get_bid_list(done_page, "12", done_txt)

print "start at time:", ctime()
main()
print "done at time:", (time.time() - start)
