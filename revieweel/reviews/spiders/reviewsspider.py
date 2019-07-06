# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from urllib.parse import urljoin
from scrapy_redis.spiders import RedisSpider, RedisCrawlSpider


# class ReviewsspiderSpider(scrapy.Spider):
from revieweel.reviews.items import ReviewsItem


class ReviewsspiderSpider(RedisCrawlSpider):
    name = 'reviewsspider'
    allowed_domains = ['www.amazon.cn']
    # start_urls = ['https://www.amazon.cn/%E6%88%91%E7%9A%84%E7%AC%AC%E4%B8%80%E6%9C%AC%E4%B8%93%E6%B3%A8%E5%8A%9B%E8%AE%AD%E7%BB%83%E4%B9%A6-%E7%BE%8E%E5%9B%BD%E8%BF%AA%E5%A3%AB%E5%B0%BC%E5%85%AC%E5%8F%B8/product-reviews/B0083DP0CY/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews']
    redis_key = 'reviews:start_urls'
    def parse(self, response):
        #print(response.text)
        #reviews_list = response.xpath("//div[@class='a-section review-views celwidget']/div")
        item = ReviewsItem()
        selector = Selector(response)
        Reviews = selector.xpath('//div[@class="a-section a-spacing-none review-views celwidget"]/div')
        for eachreview in Reviews:
            item['username'] = eachreview.xpath('.//div[@class="a-profile-content"]//span/text()').extract_first()
            item['usertitle'] = eachreview.xpath('.//div[@class="a-row"]//a[@class="a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"]//span/text()').extract_first()
            item['userreview'] = eachreview.xpath('.//span[@class="a-size-base review-text review-text-content"]//span/text()').extract_first()
            item['userdate'] = eachreview.xpath('.//span[@class="a-size-base a-color-secondary review-date"]/text()').extract_first()
            userstar = eachreview.xpath('.//div[@class="a-row"]//a[1]//i//span/text()').extract_first()
            if userstar:
                item['userstar']=userstar[0:1]
            if item['username']:
                print("".join(item['username'].split()))
                yield item
        nextLink = selector.xpath('//ul[@class="a-pagination"]//li[@class="a-last"]/a/@href').extract()
              # 第10页是最后一页，没有下一页的链接
        if nextLink:
            nextLink = nextLink[0]
            yield Request(urljoin(response.url, nextLink), callback=self.parse)
        print(response.request)
        print(response.request.headers['User-Agent'])

# lpush reviews:start_urls https://www.amazon.cn/Apple-%E8%8B%B9%E6%9E%9C-%E6%89%8B%E6%9C%BA-iPhone-X-%E6%B7%B1%E7%A9%BA%E7%81%B0%E8%89%B2-64G/product-reviews/B075L9T8HF/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews