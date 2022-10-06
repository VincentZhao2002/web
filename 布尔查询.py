import jieba
import os
from bs4 import BeautifulSoup
import csv

path = 'D:\sophomore year\gsai暑期集训\hqjthtml\\'
html_name = [file for file in os.listdir(path) if os.path.splitext(file)[1] == '.html']


def get_txt(html_path):
    try:
        with open(html_path, encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html5lib')
            # print(soup.find('h1').text + '=====')
            # print(soup.title.string)
            # tags = soup.find_all('p')
            with open(html_path[0:-5] + '.txt', 'a', encoding='utf-8') as file:
                # for tag in tags:
                # print(tag.text)
                file.writelines('\n' + soup.find('h1').text)

    except:
        pass


collections = [file for file in os.listdir(path) if os.path.splitext(file)[1] == '.txt']

"""
# 判断分词是否符合标准
def judge_word(word):
    if len(word.strip()) <= 1:
        return 0
    elif word in stop_words:
        return 0
    elif word.encode('utf-8').isalpha():
        return 0
    elif word.encode('utf-8').isdigit():
        return 0
    return 1


stop_words = []  # 构建停用词表
with open('百度停用词表.txt', 'r', encoding='utf-8') as f:
    for word in f.read():
        stop_words.append(word)
with open('中文停用词表.txt', 'r', encoding='utf-8') as f:
    for word in f.read():
        stop_words.append(word)


term_docid_pairs = []
for docid, filename in enumerate(collections):
    with open(os.path.join('hqjthtml', filename), encoding='utf-8') as fin:
        for term in jieba.cut(fin.read()):
            if not judge_word(term):
                continue
            term_docid_pairs.append((term, docid))

print(term_docid_pairs[0])
print('...')
print(term_docid_pairs[-5:])

with open('pairs.csv', 'w', encoding='utf-8') as f:
    for term in term_docid_pairs:
        csvwriter = csv.writer(f)
        csvwriter.writerow(term)
"""
# 注意此处以utf-8格式存入csv文件中后 打开表格时默认以gbk编码所以显示乱码
term_docid_pairs = []
with open('pairs.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 1:
            term_docid_pairs.append((row))
# """


term_docid_pairs = sorted(term_docid_pairs)
special_doc_id = -1
from collections import defaultdict

inverted_index = defaultdict(lambda: [special_doc_id])

for term, docid in term_docid_pairs:
    postings_list = inverted_index[term]
    if docid != postings_list[-1]:
        postings_list.append(docid)


# 一个简单的查询函数，返回collections包含查询词term的文件的文件名
def query(inverted_index, collections, query_term):
    docid_list = inverted_index[query_term][1:]  # 删去开头的-1
    results = [collections[int(docid)] for docid in docid_list]
    urls = []
    for result in results:
        with open(path + result, 'r', encoding='utf-8') as f:
            urls.append(f.readline())
    print(urls)
    return results


def output_results(query, query_func=query):
    print('query: %s, results: %s' % (query, query_func(inverted_index, collections, query)))


def intersection(l1, l2):
    answer = []
    p1, p2 = iter(l1), iter(l2)
    try:
        docID1, docID2 = next(p1), next(p2)
        while True:
            if docID1 == docID2:
                answer.append(docID1)
                docID1, docID2 = next(p1), next(p2)
            elif docID1 < docID2:
                docID1 = next(p1)
            else:
                docID2 = next(p2)
    except StopIteration:
        pass
    return answer


# 支持任意多个逻辑与查询
# 将多个查询以tuple或list的形式传递给queries参数


def logic_and_query(inverted_index, collections, queries):
    # 第一个query的结果
    l1 = inverted_index[queries[0]][1:]
    for q in queries[1:]:
        l2 = inverted_index[q][1:]
        l1 = intersection(l1, l2)
    results = [collections[int(docid)] for docid in l1]
    urls = []
    for result in results:
        with open(path + result, 'r', encoding='utf-8') as f:
            urls.append(f.readline())
    print(urls)
    return results


def logic_or_query(inverted_index, collections, queries):
    l1 = inverted_index[queries[0]][1:]
    for q in queries[1:]:
        l2 = inverted_index[q][1:]
        l1 += l2
    results = [collections[int(docid)] for docid in l1]
    urls = []
    for result in results:
        with open(path + result, 'r', encoding='utf-8') as f:
            urls.append(f.readline())
    print(urls)
    return results


question_words = jieba.lcut('疫情封校疫情品园')

output_results('宋')
output_results(question_words, query_func=logic_and_query)
