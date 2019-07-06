#! /bin/env python
# -*- coding: utf-8 -*-
"""
预测
"""
import jieba
import pymysql
import numpy as np
from gensim.models.word2vec import Word2Vec
from gensim.corpora.dictionary import Dictionary
from keras.preprocessing import sequence

from pyecharts import Pie
import yaml
from keras.models import model_from_yaml
np.random.seed(1337)  # For Reproducibility
import sys
sys.setrecursionlimit(1000000)

# define parameters
maxlen = 100
pos = 0
neu = 0
neg = 0
negpos = 0
positivefinal = 0

def create_dictionaries(model=None,
                        combined=None):
    ''' Function does are number of Jobs:
        1- Creates a word to index mapping
        2- Creates a word to vector mapping
        3- Transforms the Training and Testing Dictionaries

    '''
    if (combined is not None) and (model is not None):
        gensim_dict = Dictionary()
        gensim_dict.doc2bow(model.wv.vocab.keys(),
                            allow_update=True)
        #  freqxiao10->0 所以k+1
        w2indx = {v: k+1 for k, v in gensim_dict.items()}#所有频数超过10的词语的索引,(k->v)=>(v->k)
        w2vec = {word: model[word] for word in w2indx.keys()}#所有频数超过10的词语的词向量, (word->model(word))

        def parse_dataset(combined): # 闭包-->临时使用
            ''' Words become integers
            '''
            data=[]
            for sentence in combined:
                new_txt = []
                for word in sentence:
                    try:
                        new_txt.append(w2indx[word])
                    except:
                        new_txt.append(0) # freqxiao10->0
                data.append(new_txt)
            return data # word=>index
        combined=parse_dataset(combined)
        combined= sequence.pad_sequences(combined, maxlen=maxlen)#每个句子所含词语对应的索引，所以句子中含有频数小于10的词语，索引为0
        return w2indx, w2vec,combined
    else:
        print('No data provided...')


def input_transform(string):
    words=jieba.lcut(string)
    words=np.array(words).reshape(1,-1)
    model=Word2Vec.load('../model/Word2vec_model.pkl')
    _,_,combined=create_dictionaries(model,words)
    return combined


def lstm_predict(string, userstar):
    print('loading model......')
    with open('../model/lstm.yml', 'r') as f:
        yaml_string = yaml.load(f)
    model = model_from_yaml(yaml_string)

    print('loading weights......')
    model.load_weights('../model/lstm.h5')
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',metrics=['accuracy'])
    data=input_transform(string)
    data.reshape(1,-1)
    #print data
    result=model.predict_classes(data)
    # print result # [[1]]
    if result[0]==1:
        global pos
        pos = pos + 1
        print(string,' positive')
    elif result[0]==0:
        global neu
        neu = neu + 1
        print(string,' neural')
    else:
        if userstar >= 3:
            global negpos
            negpos = negpos + 1
            print(string, ' positive')
        else:
            global neg
            neg = neg + 1
            print(string,' negative')
    global positivefinal
    positivefinal = pos + negpos


if __name__=='__main__':
    # string='酒店的环境非常好，价格也便宜，值得推荐'
    # string='手机质量太差了，傻逼店家，赚黑心钱，以后再也不会买了'
    # string = "这是我看过文字写得很糟糕的书，因为买了，还是耐着性子看完了，但是总体来说不好，文字、内容、结构都不好"
    # string = "虽说是职场指导书，但是写的有点干涩，我读一半就看不下去了！"
    # string = "书的质量还好，但是内容实在没意思。本以为会侧重心理方面的分析，但实际上是婚外恋内容。"
    # string = "不是太好"
    # string = "不错不错"
    # string = "真的一般，没什么可以学习的"

    config = {
        'host': "127.0.0.1",
        'user': "root",
        'password': "1021",
        'db': "db_reviews",
        'charset': 'utf8mb4'
    }

    conn = pymysql.connect(**config)
    cur = conn.cursor()
    cur.execute('select userreview, userstar from reviews')
    for userreview,userstar in cur.fetchmany(size=200):
        lstm_predict(''.join(userreview), userstar)
    cur.close()
    conn.close()
    print(positivefinal)
    print(neu)
    print(neg)

    # global positivefinal
    # positivefinal = 195
    #
    # global neu
    # neu = 1
    # #
    # global neg
    # neg = 4

    # emotionList = ['positive', 'neutral', 'negative']
    # emotionNumList = [positivefinal, neu, neg]
    # print(emotionNumList)
    # pie = Pie("情感分析饼状图")
    # pie.add("", emotionList, emotionNumList, is_label_show=True)
    # pie.render('../home/web/pieEmotion.html')