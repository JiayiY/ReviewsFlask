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

tagsA = jieba.analyse.extract_tags(reviewtext, topK=10, allowPOS='a')    #allowPOS是选择提取的词性，a是形容词
tagsN = jieba.analyse.extract_tags(reviewtext, topK=10, allowPOS='n')    #allowPOS='n'，提取名词
print(" ".join(tagsA))
print(" ".join(tagsN))

#获取关键词
stopwords = []
for word in open("./data/ChineseStopWords.txt", "r", encoding='utf-8'):
    stopwords.append(word.strip())
print(stopwords)
stayed_line = ""
for word in seg_list:
    if word not in stopwords:
        stayed_line += word + " "
print(stayed_line)
#保存语料
#file = open('./data/corpus.txt', 'wb')
#file.write(stayed_line.encode("utf-8"))
#file.close()


# sentences = word2vec.Text8Corpus('./data/corpus.txt')  # 加载刚刚制作好的语料
# model = word2vec.Word2Vec(sentences, size=200, min_count=1, window=5)  # 默认window=5
#
# commit_index = pd.DataFrame(columns=['commit', 'similarity'], index=np.arange(100))
#
# index = 0
# for i in tagsN:
#     for j in tagsA:
#         commit_index.loc[index, :] = [i+j, model.similarity(i, j)]
#         index += 1
# #print(commit_index)
# comit_index_final = commit_index.sort_values(by='similarity', ascending=False)
# comit_index_final.index = commit_index.index
#
# #print(commit_index)
# print(comit_index_final)
