import pymysql
import numpy as np
from pyecharts import Line
from pyecharts import Bar
from pyecharts import Line,EffectScatter,Overlap
from pyecharts import Pie

from reviews.visualDateSale import VisualDateSale


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