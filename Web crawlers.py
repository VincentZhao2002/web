from bs4 import BeautifulSoup
import requests
import time
from url_normalize import url_normalize
from urllib.parse import urljoin


# 输入一个html文档，返回所有urls
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
        return None


headers = {'user-agent': 'my-app/0.0.1'}

# 初始化队列
queue = []
# 全局urls集合
all_urlset = set()
for url in input_urls:
    if url not in all_urlset:
        queue.append(url)
        all_urlset.add(url)

count = 0
wait_time = 0.001
htmlpath = r"D:\sophomore year\gsai暑期集训\hqjthtml\\"
used_urlset = set()
while len(queue) > 0:  # 控制迭代次数

    url = queue.pop(0)
    print(queue.__len__())  # 弹出队前一个url
    if not url.startswith('http://hqjt'):
        print(url)
        print(queue.__len__())
        continue
    used_urlset.add(url)
    html_doc = get_html(url, headers=headers)  # 从给定的url中获取html文档
    if html_doc is None:
        continue
    url_sets = crawl_all_urls(html_doc, url)  # 第一天实现的方法 crawl_all_urls: 输入一个html文档，返回所有urls
    # print(url_sets)
    for new_url in url_sets:
        # is_duplicated = judge_duplicated(new_url, all_urlset)  #判断新url是否重复
        if new_url not in all_urlset and not new_url.endswith('.pdf') and not new_url.endswith('.doc')\
                and not new_url.endswith('jpg'):
            queue.append(new_url)  # 若不重复，加入队列
            all_urlset.add(new_url)

    if wait_time > 0:
        print("等待{}秒后开始抓取".format(wait_time))
        time.sleep(wait_time)

    # 保存当前html_doc，防止被封锁
    count = count + 1
    path = htmlpath + str(count) + ".html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_doc)
        f.close()
    path = htmlpath + str(count) + ".txt"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(url)
        f.close()
    print(all_urlset.__len__())

print(all_urlset)
print(all_urlset.__len__())
