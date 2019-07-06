import pymysql
from pyecharts import Line
from pyecharts import Bar
from pyecharts import Line,EffectScatter,Overlap
from pyecharts import Pie
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
cur.execute('select userstar from reviews')
#result1 = cur.fetchall()
starCount = {}
for userstar in cur.fetchmany(size=4805):
    starCount.setdefault(userstar, 0)
    starCount[userstar] = starCount[userstar] + 1
print(starCount.values())
print(sorted(starCount.keys()))
starDict = dict(sorted(starCount.items(), key=lambda item: item[0]))
print(starDict)
gradeList = ['1','2','3','4','5']
countList = list(starDict.values())
print(gradeList, countList)
cur.close()
conn.close()
# score = list(starCount.keys())
# newScore = list(reversed(score))
# scoreCount = list(starCount.values())
# newScoreCount = list(reversed(scoreCount))
# print(score, newScore, scoreCount, newScoreCount)


# bar = Bar("评分统计折线图")
# bar.add("评分", gradeList, countList, is_smooth=True, mark_line=["max", "average"])
# #bar.show_config()
# #line.render('./htmlop/scatter02.htmlop')
# #line.render(path='./img/snapshot.png')
# #make_a_snapshot('./htmlop/scatter02.htmlop', './img/test.png')
# bar.render('./home/web/barGrade.html')
#
# pie = Pie("评分统计折线图")
# pie.add("", gradeList, countList, is_label_show=True)
# pie.render('./home/web/pieGrade.html')

