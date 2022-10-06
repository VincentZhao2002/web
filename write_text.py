import jieba
import os
from bs4 import BeautifulSoup
import csv

path = 'D:\sophomore year\gsai暑期集训\hqjthtml\\'
html_name = [file for file in os.listdir(path) if os.path.splitext(file)[1] == '.html']


def write_txt(html_path):
    try:
        with open(html_path, encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html5lib')
            # print(soup.find('h1').text + '=====')
            # print(soup.title.string)
            # tags = soup.find_all('p')
            with open(html_path[0:-5] + '.txt', 'a', encoding='utf-8') as file:
                # for tag in tags:
                # print(tag.text)
                file.writelines('\n' + soup.find('h2').text)

    except:
        pass


print(html_name)
for html in html_name:
    write_txt(path + html)