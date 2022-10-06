import jieba
import os
import dill as pickle

with open('./inverted_index.pkl', 'rb') as fin:
    restore_inverted_index = pickle.load(fin)
# print(restore_inverted_index)
with open('./doc_length.pkl', 'rb') as fin:
    doc_length = pickle.load(fin)
with open('./word_df.pkl', 'rb') as fin:
    word_df = pickle.load(fin)
with open('./terms.pkl', 'rb') as fin:
    terms = pickle.load(fin)

# 倒排索引构建样例
# 找出所有教师信息正文信息
collections = [file for file in os.listdir('hqjthtml') if os.path.splitext(file)[1] == '.txt']
# print(collections)


# 依次打开每个保存正文信息的文本文件，分词，构造term_docid_pairs,计算文档长度
term_docid_pairs = []

path = 'D:\sophomore year\gsai summer\hqjthtml\\'
from collections import Counter
import numpy as np


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

doc_length = {}
headers = []
word_df = {}  # 储存每个词的df
terms = []  # 储存所有的分词结果
for docid, filename in enumerate(collections):  # 获得每个词的df
    try:
        with open(os.path.join('hqjthtml', filename), encoding='utf-8') as fin:
            terms.append([term for term in jieba.cut(fin.read()) if judge_word(term) == 1])  # 必要的过滤
            terms_set = set(terms[docid])
            for term in terms_set:
                term_docid_pairs.append((term, docid))
                word_df[term] = word_df.get(term, 0) + 1
    except:
        pass

for docid, filename in enumerate(collections):
    try:
        N = word_df.__len__()
        term_counts = np.array(list(Counter(terms[docid]).values()))
        log_tf = np.vectorize(lambda x: 1.0 + np.log(x) if x > 0 else 0.0)
        tf = log_tf(term_counts)
        term_idf = np.array([])
        for word in set(terms[docid]):
            term_idf = np.append(term_idf, word_df[word])
        log_idf = np.vectorize(lambda n, df: np.log(n / df) if df > 0 else 0.0)
        idf = log_idf(N, term_idf)
        w = []
        for i in range(len(tf)):
            w.append(tf[i] * idf[i])
        doc_length[docid] = np.sqrt(np.sum(np.array(w) ** 2))
    except:
        pass

# 排序
# 默认情况下两个tuple比较大小就是先按照第一个元素比较，再按照第二个元素比较，因此不需要用key=lambda x:...的方式定义排序方式。
term_docid_pairs = sorted(term_docid_pairs)


# 构造倒排索引
# postings list中每一项为一个Posting类对象
class Posting(object):
    special_doc_id = -1

    def __init__(self, docid, tf=0, idf=0):
        self.docid = docid
        self.tf = tf

    def __repr__(self):
        return "<docid: %d, tf: %d>" % (self.docid, self.tf)


# 为了编程实现方便，我们在每个postings list开头加上了一个用来标记开头的Posting(special_doc_id=-1, 0)（正常docid从0编号）
# 注意这段代码只有在term_docid_pairs已排序的时候才是正确的
from collections import defaultdict

inverted_index = defaultdict(lambda: [Posting(Posting.special_doc_id, 0)])

for term, docid in term_docid_pairs:
    postings_list = inverted_index[term]
    if docid != postings_list[-1].docid:
        postings_list.append(Posting(docid, 1))
    else:
        postings_list[-1].tf += 1

inverted_index = dict(inverted_index)


# print(inverted_index)
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


def output_results(query, query_func=query, inverted_index=inverted_index):
    print('query: %s, results: %s' % (query, query_func(inverted_index, collections, query)))


def get_postings_list(inverted_index, query_term):
    try:
        return inverted_index[query_term][1:]
    except KeyError:
        return []


tf = np.vectorize(lambda x: 1.0 + np.log10(x) if x > 0 else 0.0)


def cosine_scores(inverted_index, doc_length, query, k=3):
    scores = defaultdict(lambda: 0.0)  # 保存分数
    query_terms = Counter(term for term in jieba.cut(query) if judge_word(term) == 1)  # 对查询进行分词
    N = word_df.__len__()
    for q in query_terms:
        try:
            w_tq = tf(query_terms[q])
            w_tq = w_tq * np.log10(N / word_df[q])
            postings_list = get_postings_list(inverted_index, q)
            for posting in postings_list:
                w_td = tf(posting.tf)
                w_td = w_td * np.log10(N / word_df[q])
                scores[posting.docid] += w_td * w_tq
        except:
            continue
    results = [(docid, score / doc_length[docid]) for docid, score in scores.items()]
    results.sort(key=lambda x: -x[1])
    return results[0:k]


def retrieval_by_cosine_sim(inverted_index, collections, query, k=20):
    top_scores = cosine_scores(inverted_index, doc_length, query, k=k)
    results = [(collections[docid], score) for docid, score in top_scores]
    urls = []
    for result in results:
        with open(path + result[0], 'r', encoding='utf-8') as f:
            urls.append(f.readline())
    print(urls)
    return results


fout = open('./term_docid_pairs.pkl', 'wb')
pickle.dump(term_docid_pairs, fout)
fout.close()

# output_results('营运工作的质量直接影响着学校的形象', query_func=retrieval_by_cosine_sim,
# inverted_index=restore_inverted_index)
