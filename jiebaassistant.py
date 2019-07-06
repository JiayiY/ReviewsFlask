#encoding=utf-8
import jieba
import jieba.analyse
import pymysql
import wordcloud
from scipy.misc import imread
import pandas as pd
import numpy as np
import logging
import codecs
from gensim.models import word2vec

from collections import Counter
config = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "1021",
    'db': "db_reviews",
    'charset': 'utf8mb4'
}
conn = pymysql.connect(**config)
#conn = pymysql.connect(host='127.0.0.1', port='3306', user='root', passwd='1021', db='doubanmovie', charset='utf8')
cur = conn.cursor()
cur.execute('select userreview from reviews')
#result1 = cur.fetchall()
reviewtext = ''
for userreview in cur.fetchmany(size=230):
    reviewtext = reviewtext+(''.join(userreview).replace(' ', ''))
    #reviewtext.replace('\n', '').replace('，', '')
print(reviewtext)
cur.close()
conn.close()

seg_list = jieba.lcut(reviewtext, cut_all=False)
print("Default Mode: " + "/".join(seg_list))  # 精确模式

tagsA = jieba.analyse.extract_tags(reviewtext, allowPOS='a')    #allowPOS是选择提取的词性，a是形容词
# tagsN = jieba.analyse.extract_tags(reviewtext, topK=10, allowPOS='n')    #allowPOS='n'，提取名词
# print(" ".join(tagsA))
# print(" ".join(tagsN))
print(tagsA)
#获取关键词
stopwords = []
for word in open("revieweel/reviews/data/ChineseStopWords.txt", "r", encoding='utf-8'):
    stopwords.append(word.strip())
print(stopwords)

stayed_line = ""
word_lst = []
for word in seg_list:
    if word not in stopwords:
        stayed_line += word +","
        word_lst.append(word)
print(stayed_line)
print(word_lst)

d = Counter(word_lst)
wordfinal = dict()
for wmap in d.most_common(10):
    print(wmap)
    print(wmap[0])
    wordfinal[wmap[0]] = wmap[1]
print(wordfinal)

