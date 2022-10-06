from bs4 import BeautifulSoup
import requests
import time
from url_normalize import url_normalize
from urllib.parse import urljoin
import threading


def crawl_all_urls(html_doc, url):
    all_links = set()
    try:
        soup = BeautifulSoup(html_doc, 'html.parser')
    except:
        print("Fail to parse the html document!")
        return all_links
    for anchor in soup.find_all('a'):
        href = anchor.attrs.get("href")
        if (href != "" and href != None):
            if not href.startswith('http'):
                # href = url + href
                href = urljoin(url, href)
            all_links.add(url_normalize(href))
    return all_links


# 输入种子urls
input_urls = ['http://hqjt.ruc.edu.cn/']


# 从给定的url中获取html文档
def get_html(uri, headers={}, timeout=2):
    try:
        r = requests.get(uri, headers=headers, timeout=timeout)
        r.raise_for_status()
        r.encoding = 'UTF-8'
        return r.text
    except:
        print("failed")
        print(uri)
        return None


def craw():
    global queue # 线程间共用队列
    lock.acquire()
    while len(queue) > 0:  # 控制迭代次数
        global count  # 线程间共用计数变量
        count = count + 1
        url = queue.pop(0)  # 弹出队前一个url
        print(queue.__len__())
        if not url.startswith('http://hqjt'):  # 筛选url
            print(queue.__len__())
            pool_sema.release()
            continue
        used_urlset.add(url)
        html_doc = get_html(url, headers=headers)  # 从给定的url中获取html文档
        if html_doc is None:
            pool_sema.release()
            continue
        url_sets = crawl_all_urls(html_doc, url)  # 第一天实现的方法 crawl_all_urls: 输入一个html文档，返回所有urls
        for new_url in url_sets:
            if new_url not in all_urlset and not new_url.endswith('.pdf') and not new_url.endswith('.doc'):
                queue.append(new_url)  # 若不重复，加入队列
                all_urlset.add(new_url)

        if wait_time > 0:
            print("等待{}秒后开始抓取".format(wait_time))
            time.sleep(wait_time)

        # 保存当前html_doc，防止被封锁
        path = htmlpath + str(count) + ".html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_doc)
            f.close()
        print(all_urlset.__len__())
    lock.release()
    pool_sema.release()


if __name__ == '__main__':
    headers = {'user-agent': 'my-app/0.0.1'}

    # 初始化队列
    queue = []
    # 全局urls集合
    all_urlset = set()
    for url in input_urls:
        if url not in all_urlset:
            queue.append(url)
            all_urlset.add(url)

    wait_time = 0.1
    htmlpath = r"D:\sophomore year\gsai暑期集训\hqjthtml-mul\\"
    used_urlset = set()
    count = 0
    thread_list = []
    lock = threading.Lock()
    max_connections = 10
    pool_sema = threading.Semaphore(max_connections)
    for i in range(10):
        pool_sema.acquire()
        thread = threading.Thread(target=craw)
        thread.start()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
