import time

from flask import Flask, render_template, json, request
import subprocess
import os

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


import redis
import jieba
from gensim.models.word2vec import Word2Vec
from gensim.corpora.dictionary import Dictionary
from keras.preprocessing import sequence
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

from revieweel.reviews.visualDateSale import VisualDateSale

app = Flask(__name__)

def all_np(arr):
    arr = np.array(arr)
    key = np.unique(arr)
    result = {}
    for k in key:

        mask = (arr == k)
        arr_new = arr[mask]
        v = arr_new.size
        result[k] = v
    return result



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
    model=Word2Vec.load('revieweel/reviews/model/Word2vec_model.pkl')
    _,_,combined=create_dictionaries(model,words)
    return combined


def lstm_predict(string, userstar):
    print('loading model......')
    with open('revieweel/reviews/model/lstm.yml', 'r') as f:
        yaml_string = yaml.load(f)
    model = model_from_yaml(yaml_string)

    print('loading weights......')
    model.load_weights('revieweel/reviews/model/lstm.h5')
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




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrapy')
def show_scrapy():
    return render_template('startscrapy.html')

@app.route('/contact')
def contact_me():
    return render_template('contact.html')

@app.route('/star')
def show_StarLine():
    config = {
        'host': "127.0.0.1",
        'user': "root",
        'password': "1021",
        'db': "db_reviews",
        'charset': 'utf8'
    }
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    cur.execute('select userdate from reviews')
    yearSaleList = list()
    monthlist = list()
    daylist = list()
    Count = {}
    datelist = {}
    for userdate in cur.fetchmany(size=4806):
        yearSaleList.append(userdate[0].split('年')[0])
        monthlist.append(userdate[0].split('月')[0])
    cur.close()
    conn.close()
    # print(yearlist)
    yearSaleDict = all_np(yearSaleList) #年销量字典 {'2012': 526, '2013': 1509, '2014': 1292, '2015': 641, '2016': 296, '2017': 323, '2018': 185, '2019': 34}
    print(yearSaleDict)
    years = list(yearSaleDict.keys()) #所有有销量的年份 ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    print(years)
    # print(monthlist)
    monthSaleDict = all_np(monthlist)
    print(monthSaleDict) #每年每月的销量 {'2012年10': 67, '2012年11': 75, '2012年12': 80, '2012年6': 33, '2012年7': 92, '2012年8': 85, '2012年9': 94, '2013年1': 115, '2013年10': 124, '2013年11': 186, '2013年12': 137, '2013年2': 73, '2013年3': 110, '2013年4': 127, '2013年5': 124, '2013年6': 147, '2013年7': 121, '2013年8': 127, '2013年9': 118, '2014年1': 142, '2014年10': 94, '2014年11': 70, '2014年12': 73, '2014年2': 103, '2014年3': 145, '2014年4': 121, '2014年5': 131, '2014年6': 119, '2014年7': 110, '2014年8': 104, '2014年9': 80, '2015年1': 61, '2015年10': 45, '2015年11': 49, '2015年12': 37, '2015年2': 45, '2015年3': 60, '2015年4': 62, '2015年5': 66, '2015年6': 66, '2015年7': 67, '2015年8': 45, '2015年9': 38, '2016年1': 32, '2016年10': 22, '2016年11': 32, '2016年12': 19, '2016年2': 36, '2016年3': 46, '2016年4': 32, '2016年5': 15, '2016年6': 15, '2016年7': 18, '2016年8': 16, '2016年9': 13, '2017年1': 13, '2017年10': 16, '2017年11': 26, '2017年12': 14, '2017年2': 20, '2017年3': 37, '2017年4': 46, '2017年5': 34, '2017年6': 28, '2017年7': 32, '2017年8': 32, '2017年9': 25, '2018年1': 17, '2018年10': 15, '2018年11': 18, '2018年12': 12, '2018年2': 15, '2018年3': 18, '2018年4': 23, '2018年5': 24, '2018年6': 7, '2018年7': 8, '2018年8': 15, '2018年9': 13, '2019年1': 11, '2019年2': 4, '2019年3': 6, '2019年4': 13}
    VDSList = list()
    for yy in years:
        vdsMonthSale = dict()
        vDS = VisualDateSale(yy, vdsMonthSale)
        for mk in monthSaleDict.keys():
            if yy == mk.split('年')[0]:
                vdsMonthSale[mk.split('年')[1]] = monthSaleDict[mk]
        vDS.monthSale = vdsMonthSale
        vDS.print_visualDateSale()
        VDSList.append(vDS)
    #字典+字典 {'2012': {'10': 67, '11': 75, '12': 80, '6': 33, '7': 92, '8': 85, '9': 94}, '2013': {'1': 115, '10': 124, '11': 186, '12': 137, '2': 73, '3': 110, '4': 127, '5': 124, '6': 147, '7': 121, '8': 127, '9': 118}, '2014': {'1': 142, '10': 94, '11': 70, '12': 73, '2': 103, '3': 145, '4': 121, '5': 131, '6': 119, '7': 110, '8': 104, '9': 80}, '2015': {'1': 61, '10': 45, '11': 49, '12': 37, '2': 45, '3': 60, '4': 62, '5': 66, '6': 66, '7': 67, '8': 45, '9': 38}, '2016': {'1': 32, '10': 22, '11': 32, '12': 19, '2': 36, '3': 46, '4': 32, '5': 15, '6': 15, '7': 18, '8': 16, '9': 13}, '2017': {'1': 13, '10': 16, '11': 26, '12': 14, '2': 20, '3': 37, '4': 46, '5': 34, '6': 28, '7': 32, '8': 32, '9': 25}, '2018': {'1': 17, '10': 15, '11': 18, '12': 12, '2': 15, '3': 18, '4': 23, '5': 24, '6': 7, '7': 8, '8': 15, '9': 13}, '2019': {'1': 11, '2': 4, '3': 6, '4': 13}}
    vdsdictMonthList = ['1','2','3','4','5','6','7','8','9','10','11','12']
    monSaleList = list()
    for vds in VDSList:
        vdsCompleteMSDict = dict()
        for mm in vdsdictMonthList:
            if mm in vds.monthSale.keys():
                vdsCompleteMSDict[mm] = vds.monthSale[mm]
            else:
                vdsCompleteMSDict[mm] = 0
        vds.monthSale = vdsCompleteMSDict
        print(list(vdsCompleteMSDict.values()))
        monSaleList.append(list(vdsCompleteMSDict.values()))
    print(monSaleList)

    monSaleDict = dict()
    month = 0
    for yy in years:
        monSaleDict[yy] = monSaleList[month]
        month = month + 1
    print(monSaleDict)
    vdsdictMonthListCN = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']





#star星级数量
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    cur.execute('select userstar from reviews')
    starCount = {}
    for userstar in cur.fetchmany(size=4805):
        starCount.setdefault(userstar, 0)
        starCount[userstar] = starCount[userstar] + 1
    cur.close()
    conn.close()
    print(starCount.values())
    print(sorted(starCount.keys()))
    starDict = dict(sorted(starCount.items(), key=lambda item: item[0]))
    print(starDict)
    gradeList = ['1星', '2星', '3星', '4星', '5星']
    countList = list(starDict.values())
    print(gradeList, countList)

    return render_template('star.html', years = years, monSaleDict= monSaleDict, vdsdictMonthListCN = vdsdictMonthListCN, yearSaleList = list(yearSaleDict.values()), gradeList=gradeList, countList=countList)


@app.route('/sales')
def show_SalesLine():
    config = {
        'host': "127.0.0.1",
        'user': "root",
        'password': "1021",
        'db': "db_reviews",
        'charset': 'utf8'
    }
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    cur.execute('select userdate from reviews')
    yearSaleList = list()
    monthlist = list()
    daylist = list()
    Count = {}
    datelist = {}
    for userdate in cur.fetchmany(size=4806):
        yearSaleList.append(userdate[0].split('年')[0])
        monthlist.append(userdate[0].split('月')[0])
    cur.close()
    conn.close()
    # print(yearlist)
    yearSaleDict = all_np(yearSaleList) #年销量字典 {'2012': 526, '2013': 1509, '2014': 1292, '2015': 641, '2016': 296, '2017': 323, '2018': 185, '2019': 34}
    print(yearSaleDict)
    years = list(yearSaleDict.keys()) #所有有销量的年份 ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    print(years)
    # print(monthlist)
    monthSaleDict = all_np(monthlist)
    print(monthSaleDict) #每年每月的销量 {'2012年10': 67, '2012年11': 75, '2012年12': 80, '2012年6': 33, '2012年7': 92, '2012年8': 85, '2012年9': 94, '2013年1': 115, '2013年10': 124, '2013年11': 186, '2013年12': 137, '2013年2': 73, '2013年3': 110, '2013年4': 127, '2013年5': 124, '2013年6': 147, '2013年7': 121, '2013年8': 127, '2013年9': 118, '2014年1': 142, '2014年10': 94, '2014年11': 70, '2014年12': 73, '2014年2': 103, '2014年3': 145, '2014年4': 121, '2014年5': 131, '2014年6': 119, '2014年7': 110, '2014年8': 104, '2014年9': 80, '2015年1': 61, '2015年10': 45, '2015年11': 49, '2015年12': 37, '2015年2': 45, '2015年3': 60, '2015年4': 62, '2015年5': 66, '2015年6': 66, '2015年7': 67, '2015年8': 45, '2015年9': 38, '2016年1': 32, '2016年10': 22, '2016年11': 32, '2016年12': 19, '2016年2': 36, '2016年3': 46, '2016年4': 32, '2016年5': 15, '2016年6': 15, '2016年7': 18, '2016年8': 16, '2016年9': 13, '2017年1': 13, '2017年10': 16, '2017年11': 26, '2017年12': 14, '2017年2': 20, '2017年3': 37, '2017年4': 46, '2017年5': 34, '2017年6': 28, '2017年7': 32, '2017年8': 32, '2017年9': 25, '2018年1': 17, '2018年10': 15, '2018年11': 18, '2018年12': 12, '2018年2': 15, '2018年3': 18, '2018年4': 23, '2018年5': 24, '2018年6': 7, '2018年7': 8, '2018年8': 15, '2018年9': 13, '2019年1': 11, '2019年2': 4, '2019年3': 6, '2019年4': 13}
    VDSList = list()
    for yy in years:
        vdsMonthSale = dict()
        vDS = VisualDateSale(yy, vdsMonthSale)
        for mk in monthSaleDict.keys():
            if yy == mk.split('年')[0]:
                vdsMonthSale[mk.split('年')[1]] = monthSaleDict[mk]
        vDS.monthSale = vdsMonthSale
        vDS.print_visualDateSale()
        VDSList.append(vDS)
    #字典+字典 {'2012': {'10': 67, '11': 75, '12': 80, '6': 33, '7': 92, '8': 85, '9': 94}, '2013': {'1': 115, '10': 124, '11': 186, '12': 137, '2': 73, '3': 110, '4': 127, '5': 124, '6': 147, '7': 121, '8': 127, '9': 118}, '2014': {'1': 142, '10': 94, '11': 70, '12': 73, '2': 103, '3': 145, '4': 121, '5': 131, '6': 119, '7': 110, '8': 104, '9': 80}, '2015': {'1': 61, '10': 45, '11': 49, '12': 37, '2': 45, '3': 60, '4': 62, '5': 66, '6': 66, '7': 67, '8': 45, '9': 38}, '2016': {'1': 32, '10': 22, '11': 32, '12': 19, '2': 36, '3': 46, '4': 32, '5': 15, '6': 15, '7': 18, '8': 16, '9': 13}, '2017': {'1': 13, '10': 16, '11': 26, '12': 14, '2': 20, '3': 37, '4': 46, '5': 34, '6': 28, '7': 32, '8': 32, '9': 25}, '2018': {'1': 17, '10': 15, '11': 18, '12': 12, '2': 15, '3': 18, '4': 23, '5': 24, '6': 7, '7': 8, '8': 15, '9': 13}, '2019': {'1': 11, '2': 4, '3': 6, '4': 13}}
    vdsdictMonthList = ['1','2','3','4','5','6','7','8','9','10','11','12']
    monSaleList = list()
    for vds in VDSList:
        vdsCompleteMSDict = dict()
        for mm in vdsdictMonthList:
            if mm in vds.monthSale.keys():
                vdsCompleteMSDict[mm] = vds.monthSale[mm]
            else:
                vdsCompleteMSDict[mm] = 0
        vds.monthSale = vdsCompleteMSDict
        print(list(vdsCompleteMSDict.values()))
        monSaleList.append(list(vdsCompleteMSDict.values()))
    print(monSaleList)

    monSaleDict = dict()
    month = 0
    for yy in years:
        monSaleDict[yy] = monSaleList[month]
        month = month + 1
    print(monSaleDict)
    vdsdictMonthListCN = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']





#star星级数量
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    cur.execute('select userstar from reviews')
    starCount = {}
    for userstar in cur.fetchmany(size=4805):
        starCount.setdefault(userstar, 0)
        starCount[userstar] = starCount[userstar] + 1
    cur.close()
    conn.close()
    print(starCount.values())
    print(sorted(starCount.keys()))
    starDict = dict(sorted(starCount.items(), key=lambda item: item[0]))
    print(starDict)
    gradeList = ['1星', '2星', '3星', '4星', '5星']
    countList = list(starDict.values())
    print(gradeList, countList)

    return render_template('sales.html', years = years, monSaleDict= monSaleDict, vdsdictMonthListCN = vdsdictMonthListCN, yearSaleList = list(yearSaleDict.values()), gradeList=gradeList, countList=countList)



@app.route('/startScrapy',  methods=['GET', 'POST'])
def start_scrapy():
    scrapyUrl = request.form.get('crawlurl')

    r = redis.Redis(host='localhost', port=6379, decode_responses=True, db=1, charset='utf-8')  # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
    r.lpush("reviews:start_urls", scrapyUrl)
    print(r.lrange("reviews:start_urls", 0, -1))

    time.sleep(5)

    subprocess.check_call('python main.py', shell=True,
                          cwd='E:\\reviewanalysisgra\\ReviewsFlask\\revieweel\\reviews')


    return render_template('index.html')

@app.route('/emotion')
def show_Emotion():
    # config = {
    #     'host': "127.0.0.1",
    #     'user': "root",
    #     'password': "1021",
    #     'db': "db_reviews",
    #     'charset': 'utf8'
    # }
    # conn = pymysql.connect(**config)
    # cur = conn.cursor()
    # cur.execute('select userreview, userstar from reviews')
    # for userreview, userstar in cur.fetchmany(size=200):
    #     lstm_predict(''.join(userreview), userstar)
    # cur.close()
    # conn.close()
    # print(positivefinal)
    # print(neu)
    # print(neg)

    from collections import Counter
    config = {
        'host': "127.0.0.1",
        'user': "root",
        'password': "1021",
        'db': "db_reviews",
        'charset': 'utf8mb4'
    }
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    cur.execute('select userreview from reviews')
    # result1 = cur.fetchall()
    reviewtext = ''
    for userreview in cur.fetchmany(size=4800):
        reviewtext = reviewtext + (''.join(userreview).replace(' ', ''))
        # reviewtext.replace('\n', '').replace('，', '')
    print(reviewtext)
    cur.close()
    conn.close()

    seg_list = jieba.lcut(reviewtext, cut_all=False)
    print("Default Mode: " + "/".join(seg_list))  # 精确模式

    tagsA = jieba.analyse.extract_tags(reviewtext, allowPOS='a')  # allowPOS是选择提取的词性，a是形容词
    # tagsN = jieba.analyse.extract_tags(reviewtext, topK=10, allowPOS='n')    #allowPOS='n'，提取名词
    # print(" ".join(tagsA))
    # print(" ".join(tagsN))
    print(tagsA)
    # 获取关键词
    stopwords = []
    for word in open("revieweel/reviews/data/ChineseStopWords.txt", "r", encoding='utf-8'):
        stopwords.append(word.strip())
    print(stopwords)

    stayed_line = ""
    word_lst = []
    for word in seg_list:
        if word not in stopwords:
            stayed_line += word + ","
            word_lst.append(word)
    print(stayed_line)
    print(word_lst)

    counterword = Counter(word_lst)
    print(counterword.most_common(10))

    wordfinal = dict()
    for wmap in counterword.most_common(100):
        wordfinal[wmap[0]] = wmap[1]
    print(wordfinal)

    return render_template('emotion.html', positivefinal = 4672, neu = 48, neg =96, wordfinal = wordfinal)


if __name__ == '__main__':
    app.run(debug= True)
