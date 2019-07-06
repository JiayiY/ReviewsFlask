# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    username = scrapy.Field()  # 用户名称
    usertitle = scrapy.Field()  # 评价题目
    userreview = scrapy.Field()  # 用户评价
    userstar = scrapy.Field()    # 用户星评
    userdate = scrapy.Field()    #评论日期
    pass
