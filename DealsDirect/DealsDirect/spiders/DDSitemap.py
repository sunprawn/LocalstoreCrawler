__author__ = 'simony'
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from DealsDirect.items import DealsdirectItem
from DealsDirect import settings

class DDSitemapSpider(Spider):
    name = "DealsDirect"
    allowed_domains = "www.dealsdirect.com.au"
    start_urls = [
        "http://www.dealsdirect.com.au/%s/?sort=popularity&display=all" % s
        for s in settings.CATEGORIES
    ]


    def parse(self, response):
        count = 0
        for product in response.xpath('//div[contains(@class,"site-map")]/ul/li'):
            link = product.xpath('a/@href').extract_first()

            if link is None:
                continue
            else:
                url = self.allowed_domains + link
                count = count + 1

                #yield Request(url, callback=self.parse_product)
        self.logger.info("count is " + str(count))