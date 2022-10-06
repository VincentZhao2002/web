import jieba
import os
import dill as pickle
from collections import Counter
import numpy as np
from collections import defaultdict

# 读取已储存的信息
with open('./inverted_index.pkl', 'rb') as fin:
    restore_inverted_index = pickle.load(fin)
with open('./word_df.pkl', 'rb') as fin:
    word_df = pickle.load(fin)
with open('./terms.pkl', 'rb') as fin:
    terms = pickle.load(fin)
with open('./doc_length.pkl', 'rb') as fin:
    doc_length = pickle.load(fin)

collections = [file for file in os.listdir('hqjthtml') if os.path.splitext(file)[1] == '.txt']

path = 'D:\sophomore year\gsai summer\hqjthtml\\'


# 判断分词是否合格的函数
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


# postings list中每一项为一个Posting类对象
class Posting(object):
    special_doc_id = -1

    def __init__(self, docid, tf=0, idf=0):
        self.docid = docid
        self.tf = tf

    def __repr__(self):
        return "<docid: %d, tf: %d>" % (self.docid, self.tf)


class Results(object):
    def __init__(self, title, url):
        self.title = title
        self.url = url


# 一个简单的查询函数，返回collections包含查询词term的文件的文件名
def query(inverted_index, collections, query_term):
    postings_list = inverted_index[query_term][1:]  # 删去开头的Posting(-1, 0)
    results = [collections[posting.docid] for posting in postings_list]
    urls = []
    for result in results:
        with open(path + result, 'r', encoding='utf-8') as f:
            urls.append(f.readline())
    print(urls)
    return results


def output_results(query, query_func=query, inverted_index=restore_inverted_index):
    print('query: %s, results: %s' % (query, query_func(inverted_index, collections, query)))


def get_postings_list(inverted_index, query_term):
    try:
        return inverted_index[query_term][1:]
    except KeyError:
        return []


tf = np.vectorize(lambda x: 1.0 + np.log(x) if x > 0 else 0.0)


# 这里并没有采用向量空间计算余弦相似度的算法，而是直接累加tf-idf遍历得分
def tf_idf(inverted_index, query, k=3):
    scores = defaultdict(lambda: 0.0)  # 保存分数
    query_terms = Counter(term for term in jieba.cut(query) if judge_word(term) == 1)  # 对查询进行分词
    N = word_df.__len__()
    for q in query_terms:
        try:
            postings_list = get_postings_list(inverted_index, q)
            for posting in postings_list:
                w_td = tf(posting.tf)
                w_td = w_td * np.log10(N / word_df[q])
                scores[posting.docid] += w_td
        except:
            continue
    results = [(docid, score) for docid, score in scores.items()]
    results.sort(key=lambda x: -x[1])
    return results[0:k]


# 基于原始tf-idf加权升级后的算法
def BM25(inverted_index, query, n=3, k=1.2, b=0.75):
    scores = defaultdict(lambda: 0.0)  # 保存分数
    query_terms = Counter(term for term in jieba.cut(query) if judge_word(term) == 1)  # 对查询进行分词
    N = word_df.__len__()
    count = 0
    for length in doc_length:
        count += length
    avdl = count / len(doc_length)  # 计算平均文档长度
    for q in query_terms:
        try:
            postings_list = get_postings_list(inverted_index, q)
            for posting in postings_list:
                w_tf = tf(posting.tf)
                w_td = w_tf
                w_td = w_td * np.log(N / word_df[q])
                w_td = w_td * (k + 1) * w_tf / (w_tf + k * (1 - b + b * doc_length[posting.docid] / avdl))
                scores[posting.docid] += w_td  # 将计算后的w_td累加计算得分
        except:
            continue
    results = [(docid, score) for docid, score in scores.items()]
    results.sort(key=lambda x: -x[1])
    return results[0:n]


def retrieval_by_tf_idf(inverted_index, collections, query, k=20):
    top_scores = BM25(inverted_index, query, n=k)
    results = [(collections[docid], score) for docid, score in top_scores]
    # print(results)
    return results


def evaluate(query=''):
    results = retrieval_by_tf_idf(inverted_index=restore_inverted_index, collections=collections, query=query, )
    urls = []
    for result in results:
        with open(path + result[0], 'r', encoding='utf-8') as f:
            urls.append(f.readline().strip())
    # print(urls)
    return urls


def get_idf(word=''):
    N = word_df.__len__()
    return word_df[word] / N

# evaluate('塑造品质 启蒙希望')
