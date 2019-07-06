#encoding=utf-8
import jieba
import jieba.analyse
import pymysql
import wordcloud
from scipy.misc import imread

config = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "1021",
    'db': "db_reviews",
    'charset': 'utf8'
}
conn = pymysql.connect(**config)
#conn = pymysql.connect(host='127.0.0.1', port='3306', user='root', passwd='1021', db='doubanmovie', charset='utf8')
cur = conn.cursor()
cur.execute('select userreview from reviews')
#result1 = cur.fetchall()
reviewtext = ''
for userreview in cur.fetchmany(size=10):
    reviewtext = reviewtext+(''.join(userreview))
    #reviewtext.replace('\n', '').replace('，', '')
cur.close()
conn.close()
reviewtext.replace(' ', '')
print(reviewtext)
seg_list = jieba.cut(reviewtext, cut_all=False)
print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
#获取关键词
tags = jieba.analyse.extract_tags(reviewtext, topK=5)
print("关键词:")
print(" ".join(tags))

# p_mask = imread("test.jpg")
# W = wordcloud.WordCloud(background_color="white", mask=p_mask)
# W.generate(" ".join(tags))
# W.to_file("pic.png")
