from flask import Flask, render_template, request
from BM25 import evaluate
from bs4 import BeautifulSoup
import requests
import jieba
from BM25 import get_idf
from BM25 import judge_word
import re

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['GET'])
def query():
    key = request.args.get('key')

    urls = evaluate(key)
    results = []

    headers = {'user-agent': 'my-app/0.0.1'}

    def get_html(uri, headers=headers, timeout=None):
        try:
            r = requests.get(uri, headers=headers, timeout=timeout)
            r.raise_for_status()
            r.encoding = 'UTF-8'
            return r.text
        except:
            return None
    words = [term for term in jieba.lcut(key) if judge_word(term) == 1]
    word_idf = {}
    for term in words:
        word_idf[term] = get_idf(term)
    sorted_word = sorted(word_idf.items(), key=lambda item: item[1])

    for url in urls:
        html_txt = get_html(url)
        if html_txt is None:
            results.append({'title': '', 'url': '', 'abstract': ''})
            continue
        soup = BeautifulSoup(html_txt, features="lxml")
        title = soup.find('h1')
        pos = None
        i = 0
        while pos is None:
            pos = soup.find(string=re.compile('.*{0}.*'.format(sorted_word[i][0])), recursive=True)
            i += 1
        if title is None:
            title = soup.title
        title = title.string
        for word in words:
            title = title.replace(word, '<span style="color:red">'+word+'</span>')
            pos = pos.replace(word, '<span style="color:red">'+word+'</span>')
        tem_dict = {'title': title, 'url': url, 'abstract': pos}
        results.append(tem_dict)
    return render_template('res.html', key=key, results=results)


app.run(host='0.0.0.0', port=12345, debug=True)
